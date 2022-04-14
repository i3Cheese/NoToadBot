import datetime
from typing import Any, Iterable, Optional, Union
import yaml
import pydantic
import csv

from settings import USE_TZ
from utils import bold, escape, transform_time_for_today


class Link(pydantic.BaseModel):
    name: str
    url: str

    def __str__(self):
        name = escape(self.name)
        if self.url:
            return f'<a href="{self.url}">{name}</a>'
        else:
            return name


class Lesson(pydantic.BaseModel):
    shortname: str
    name: str
    links: list[Link]

    def __str__(self):
        s = f"{bold(self.name)}\n"
        s += ''.join(f"{link}\n" for link in self.links)
        return s


class Event(pydantic.BaseModel):
    type: str
    name: str
    start_time: datetime.time
    end_time: datetime.time

    @property
    def time_str(self):
        return escape(f'{self.start_time:%H:%M}-{self.end_time:%H:%M}')

    def __str__(self):
        s = f"{bold(self.name)} {self.time_str}\n"
        return s


class LessonEvent(Event):
    type = 'lesson'
    lesson: Lesson

    def __str__(self):
        s = f'{self.name} {bold(self.lesson.name)} {self.time_str}\n'
        s += ''.join(str(link) + '\n' for link in self.lesson.links)
        return s


def load_lessons():
    with open('lessons.yaml', 'r') as f:
        lessons = yaml.safe_load(f)
    lessons = [Lesson(**lesson) for lesson in lessons]
    return lessons


def load_timetable() -> list[list[Optional[Lesson]]]:
    lessons = load_lessons()
    lessons_dict = {lesson.shortname: lesson for lesson in lessons}
    with open('timetable.csv', mode='r', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        timetable = []
        for row in reader:
            ttrow = []
            for shortname in row:
                if not shortname:
                    ttrow.append(None)
                else:
                    ttrow.append(lessons_dict[shortname])
            timetable.append(ttrow)
    return timetable


def load_shedule() -> list[Event]:
    events = []
    with open('shedule.csv', 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row: dict[str, Any]
            events.append(Event(**row))
    return events


class SundayError(Exception):
    pass


def load_day_events(day: Optional[datetime.date] = None) -> list[Event]:
    if day is None:
        day = datetime.datetime.now(USE_TZ).date()
    weekday = day.weekday()
    if weekday == 6:
        return []
    lessons = iter(load_timetable()[weekday])
    events = load_shedule()
    res_events: list[Event] = []
    for ev in events:
        if ev.type == 'lesson':
            lesson = next(lessons)
            if lesson is None:
                ev = None
            else:
                ev = LessonEvent(**ev.dict(), lesson=lesson)
        if ev is not None:
            res_events.append(ev)
    return res_events


def join_evs(events: Iterable[Any]) -> str:
    return escape("================\n").join(map(str, events))


def get_timedelta_to_time(t: datetime.time, dt: datetime.datetime) -> datetime.timedelta:
    return transform_time_for_today(t, dt) - dt


def timedelta_to_str(td: datetime.timedelta) -> str:
    # d = {"days": td.days}
    # d["hours"], rem = divmod(td.seconds, 3600)
    d = {}
    d["minutes"], d["seconds"] = divmod(td.seconds, 60)
    return "{minutes} мин {seconds} с".format(**d)


def now_events_message(dt: Optional[datetime.datetime] = None) -> str:
    if dt is None:
        dt = datetime.datetime.now(USE_TZ)
    events = load_day_events(dt.date())

    now_events: list[Event] = []
    next_event: Optional[Event] = None
    now_time = dt.time()
    for event in events:
        if event.start_time <= now_time < event.end_time:
            now_events.append(event)
        elif now_time <= event.start_time:
            next_event = event
            break
    s = ""
    if now_events:
        s += join_evs(
            f"{e}До конца: {timedelta_to_str(get_timedelta_to_time(e.end_time, dt))}" for e in now_events
        )
    elif next_event:
        s += f"{next_event}До начала: {timedelta_to_str(get_timedelta_to_time(next_event.start_time, dt))}"
        # if s:
        #     s += "\n\n\n"
        # s += escape("Далее:\n\n")
        # s += str(next_event)
    if not s:
        s = escape("Сегодня больше ничего не будет, отдыхаем!!!")
    return s

def agenda_message(dt: Optional[datetime.datetime] = None) -> str:
    if dt is None:
        dt = datetime.datetime.now(USE_TZ)
    events = load_day_events(dt.date())
    if not events:
        return bold("Пусто :)")
    return join_evs(events)
