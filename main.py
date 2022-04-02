#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to handle '(my_)chat_member' updates.
Greets new users & keeps track of which chats the bot is in.
Usage:
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import random

import dateutil.parser
from telegram import Update
import telegram
from telegram.ext import ChatMemberHandler, CommandHandler, Updater
import telegram.ext

from agenda import agenda_message, now_events_message
from notifications import first_init, subscribe_callback, unsubscribe_callback
from secure import secure_callback
import track_chats
from utils import escape, reply_text

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename='NoToadBot.log',
)

logger = logging.getLogger(__name__)


@secure_callback
def link_asap(update: telegram.Update, context: telegram.ext.CallbackContext):
    text = now_events_message()
    assert(update.effective_message is not None)
    if (update.effective_message.text == update.effective_message.text.upper()):
        text = escape("НЕ ОРИ ПЖ!!!\n\n") + text
    logger.info(repr(text))
    reply_text(update, text)


@secure_callback
def agenda_asap(update: telegram.Update, context: telegram.ext.CallbackContext):
    text = agenda_message()
    assert(update.effective_message is not None)

    if update.effective_message is None:
        return
    if not context.args:
        text = agenda_message()
    else:
        dt = context.args[0]
        logger.info(dt)
        try:
            dt = dateutil.parser.parse(dt)
        except dateutil.parser.ParserError:
            reply_text(update, "Неправильный аргумент")
            return

        text = now_events_message(dt)

    if (update.effective_message.text == update.effective_message.text.upper()):
        text = escape("НЕ ОРИ ПЖ!!!\n") + text
    logger.info(repr(text))
    reply_text(update, text)


@secure_callback
def links_with_time(update: telegram.Update, context: telegram.ext.CallbackContext):
    if update.effective_message is None:
        return
    if not context.args:
        link_asap(update, context)
        # reply_text(update, "Пожалуйста укажите дату и время")
        return

    dt = context.args[0]
    logger.info(dt)
    try:
        dt = dateutil.parser.parse(dt)
    except dateutil.parser.ParserError:
        reply_text(update, "Неправильный аргумент")
        return

    text = now_events_message(dt)
    reply_text(update, text)

def thank_you_botik(update: telegram.Update, context: telegram.ext.CallbackContext):
    if update.effective_message is None:
        return

    messages = [
        "Мяу ^_^",
        "Квак",
        "Фыр фыр",
    ]
    text = random.choice(messages)

    reply_text(update, text)

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("5148912290:AAGEP6DbSx53l095t9geTHM5kxyjGhHyTxM")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Keep track of which chats the bot is in
    dispatcher.add_handler(ChatMemberHandler(
        track_chats.track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    dispatcher.add_handler(CommandHandler(
        "show_chats", track_chats.show_chats))

    # Handle members joining/leaving chats.
    dispatcher.add_handler(ChatMemberHandler(
        track_chats.greet_chat_members, ChatMemberHandler.CHAT_MEMBER))

    dispatcher.add_handler(telegram.ext.MessageHandler(
        telegram.ext.Filters.regex(r'(?i)ССЫЛКУ СРОЧНО'),
        link_asap,
    ))
    dispatcher.add_handler(CommandHandler(
        "link_asap", links_with_time))

    dispatcher.add_handler(telegram.ext.MessageHandler(
        telegram.ext.Filters.regex(r'(?i)РАССПИСАНИЕ СРОЧНО'),
        agenda_asap,
    ))
    dispatcher.add_handler(telegram.ext.MessageHandler(
        telegram.ext.Filters.regex(r'(?i)(спасибо|спс) (бот(ик)?|жаба|жабка)'),
        thank_you_botik,
    ))
    dispatcher.add_handler(CommandHandler(
        ["agenda_asap", "todat"], agenda_asap,
    ))

    dispatcher.add_handler(CommandHandler(
        "subscribe",
        subscribe_callback,
    ))
    dispatcher.add_handler(CommandHandler(
        "unsubscribe",
        unsubscribe_callback,
    ))

    first_init(updater.job_queue)  # initialize shedule

    # Start the Bot
    # We pass 'allowed_updates' handle *all* updates including `chat_member` updates
    # To reset this, simply pass `allowed_updates=[]`
    updater.start_polling(allowed_updates=Update.ALL_TYPES)

    updater.idle()


if __name__ == "__main__":
    main()
