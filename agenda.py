import datetime
from typing import Any, Optional
import yaml
import pydantic
import csv

from settings import USE_TZ
from telegram_markdown import bold, escape


class Link(pydantic.BaseModel):
    name: str
    url: str

    def __str__(self):
        return escape(f"{self.name}: {self.url}")


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

    def __str__(self):
        time_str = escape(f'{self.start_time:%H:%M}-{self.end_time:%H:%M}')
        s = f"{bold(self.name)} {time_str}\n"
        return s


class LessonEvent(Event):
    type = 'lesson'
    lesson: Lesson

    def __str__(self):
        s = super().__str__()
        s += str(self.lesson)
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
        raise SundayError
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


def format_event_list(events: list[Event]) -> str:
    return escape("================\n").join(map(str, events))


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
        s = escape("Сейчас идёт:\n________________\n")
        s += format_event_list(now_events)
    if next_event:
        if s:
            s += "\n\n\n"
        s += escape("Далее:\n________________\n")
        s += str(next_event)
    if not s:
        s = escape("Сейчас ничего нет, отдыхаем!!!")
    return s
