# import re

# from telegram.utils.helpers import escape as escape_html 
from typing import Optional

from html import escape as escape_html
import datetime

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
   
