from typing import Optional

from html import escape as escape_html
from telegram.constants import PARSEMODE_HTML
import telegram.ext
import telegram
import datetime
import dateutil.parser

from settings import USE_TZ


def bold(arg):
    return f"<b>{arg}</b>"


def transform_time_for_today(t: datetime.time, dt: Optional[datetime.datetime] = None):
    if dt is None:
        dt = datetime.datetime.now(USE_TZ)
    return dt.replace(
        hour=t.hour,
        minute=t.minute,
        second=t.second,
        microsecond=t.microsecond,
    )


parse_mode = PARSEMODE_HTML


def reply_text(update: telegram.Update, text: str):
    assert(update.effective_message is not None)
    update.effective_message.reply_text(
        text, parse_mode=parse_mode, disable_web_page_preview=True)


def send_text(context: telegram.ext.CallbackContext, chat_id: (int | str), text: str):
    context.bot.send_message(
        chat_id, text, parse_mode=parse_mode, disable_web_page_preview=True)


def parse_date_time(arg: str):
    try:
        change = int(arg)
        dt = datetime.datetime.now(USE_TZ) + datetime.timedelta(days=change)
    except ValueError:
        try:
            dt = dateutil.parser.parse(arg)
        except dateutil.parser.ParserError:
            raise ValueError
    return dt


reserve_characters = [
    '\\',
    '*',
    '_',
    '-',
    '!',
]


def escape(arg):
    return escape_html(arg)
    # return escape_markdown(arg, version=2)
