import re

from telegram.utils.helpers import escape_markdown

def bold(arg):
    return f"*{arg}*"


reserve_characters = [
    '\\',
    '*',
    '_',
    '-',
    '!',
]

def escape(arg):
    return escape_markdown(arg, version=2)
   
