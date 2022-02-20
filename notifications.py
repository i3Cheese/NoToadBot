import datetime
import logging
from typing import Iterable
from telegram.constants import PARSEMODE_MARKDOWN_V2
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.jobqueue import JobQueue
from telegram.update import Update

from agenda import Event, load_day_events
from secure import secure_callback
from settings import USE_TZ

logger = logging.getLogger(__name__)

subscriptors_file = 'subscriptors.txt'


def subscribe(chat_id: int) -> bool:
    subscribed_chats = get_subscribed_chats()
    if chat_id not in subscribed_chats:
        subscribed_chats.append(chat_id)
        write_subscribed_chats(subscribed_chats)
        return True
    else:
        return False


def unsubscribe(chat_id: int):
    write_subscribed_chats(
        filter(lambda x: x != chat_id, get_subscribed_chats())
    )


def write_subscribed_chats(subscribed_chats: Iterable[int]):
    with open(subscriptors_file, 'w', encoding='utf-8') as f:
        f.writelines(map(lambda s: str(s) + '\n', subscribed_chats))


def get_subscribed_chats() -> list[int]:
    try:
        with open(subscriptors_file, 'r', encoding='utf-8') as f:
            subscribed_chats = [int(s.strip()) for s in f]
    except FileNotFoundError:
        subscribed_chats = []
    return subscribed_chats


@secure_callback
def subscribe_callback(update: Update, context: CallbackContext):
    chat = update.effective_chat
    assert(chat is not None)
    chat_id = chat.id
    assert(update.effective_message is not None)

    if subscribe(chat_id):
        logger.info("%d was subscribed", chat_id)
        update.effective_message.reply_text(
            "Вы успешно подписались на рассылку"
        )
    else:
        update.effective_message.reply_text(
            "Вы и так подписаны"
        )


def unsubscribe_callback(update: Update, context: CallbackContext):
    chat = update.effective_chat
    assert(chat is not None)
    chat_id = chat.id
    unsubscribe(chat_id)
    logger.info("%d was unsubscribed", chat_id)
    assert(update.effective_message is not None)
    update.effective_message.reply_text(
        "Вы успешно отписались от рассылки"
    )


def send_notification(context: CallbackContext):
    job = context.job
    assert(job is not None)
    event: Event = job.context
    text = str(event)
    logging.info("SEND NOTIFICATION %s", event.name)
    for chat_id in get_subscribed_chats():
        try:
            context.bot.send_message(
                chat_id, text, parse_mode=PARSEMODE_MARKDOWN_V2)
        except Exception as e:
            logger.exception(e)

def transform_time_for_today(t: datetime.time):
    today = datetime.datetime.now(USE_TZ)
    return today.replace(
        hour=t.hour,
        minute=t.minute,
        second=t.second,
        microsecond=t.microsecond,
    )

    

def shedule_for_today(job_queue: JobQueue):
    events = load_day_events()
    # start_dt = datetime.datetime.now(USE_TZ) + datetime.timedelta(seconds=10)
    # end_dt = start_dt + datetime.timedelta(minutes=10)
    # events.append(Event(
    #     type='meal',
    #     name='ТЕСТ',
    #     start_time=start_dt.time(),
    #     end_time=end_dt.time(),
    # ))
    for event in events:
        job_queue.run_once(
            send_notification,
            transform_time_for_today(event.start_time),
            context=event,
        )


def daily_callback(context: CallbackContext):
    assert(context.job_queue is not None)
    shedule_for_today(context.job_queue)


def first_init(job_queue: JobQueue):
    """DONT CALL IT from 00:00 to 00:30 msk"""
    shedule_for_today(job_queue)

    job_queue.run_daily(
        daily_callback, 
        datetime.time(0, 0, 30, 0, tzinfo=USE_TZ)
    )
