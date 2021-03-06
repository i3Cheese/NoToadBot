import logging
from typing import Callable
from telegram.ext.callbackcontext import CallbackContext

from telegram.update import Update

logger = logging.getLogger(__name__)

with open("accepted_chats.txt", 'r') as f:
    accepted_chats = [int(s.split('#')[0].strip()) for s in f]


def secure_callback(func: Callable[[Update, CallbackContext], None]) -> Callable[[Update, CallbackContext], None]:
    def _func(update: Update, callback: CallbackContext):
        chat = update.effective_chat
        assert(chat is not None)
        if (chat.id not in accepted_chats):
            logger.info("%d trying to use secure command", chat.id) 
            assert(update.effective_message is not None)
            update.effective_message.reply_text("У вас нет доступа к этой команде", parse_mode='MarkdownV2')
        else:
            return func(update, callback)

    return _func


