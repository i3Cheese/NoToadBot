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
from typing import Optional, Tuple
import dateutil.parser

from telegram import Chat, ChatMember, ChatMemberUpdated, ParseMode, Update
import telegram
from telegram.ext import CallbackContext, ChatMemberHandler, CommandHandler, Updater
import telegram.ext

from agenda import now_events_message
from secure import secure_callback
import track_chats

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


@secure_callback
def link_asap(update: telegram.Update, context: telegram.ext.CallbackContext):
    text = now_events_message()
    if update.effective_message is None:
        return
    update.effective_message.reply_text(text, parse_mode='MarkdownV2')


@secure_callback
def links_with_time(update: telegram.Update, context: telegram.ext.CallbackContext):
    if update.effective_message is None:
        return
    if not context.args:
        update.effective_message.reply_text("Пожалуйста укажите дату и время")
        return

    dt = context.args[0]
    logger.info(dt)
    try:
        dt = dateutil.parser.parse(dt)
    except dateutil.parser.ParserError:
        update.effective_message.reply_text("Неправильный аргумент")
        return

    text = now_events_message(dt)
    update.effective_message.reply_text(text, parse_mode='MarkdownV2')


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("5148912290:AAGEP6DbSx53l095t9geTHM5kxyjGhHyTxM")
    updater.job_queue

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

    # Start the Bot
    # We pass 'allowed_updates' handle *all* updates including `chat_member` updates
    # To reset this, simply pass `allowed_updates=[]`
    updater.start_polling(allowed_updates=Update.ALL_TYPES)

    updater.idle()


if __name__ == "__main__":
    main()
