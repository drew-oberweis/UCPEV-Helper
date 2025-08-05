import logging
import time
import os
import sys

from telegram import (
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
)

import user_commands
import admin_commands
import data

import environment_handler
import utils

logger = logging.getLogger(__name__)
token = environment_handler.get_telegram_token()

def do_nothing():
    return None

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user = update.effective_user
    username = user.username

    # ignore if private chat
    if(update.effective_chat.type == "private"):
        return do_nothing()
    
    if(username == None):
        try:
            username = user.first_name + " " + user.last_name
        except:
            username = user.first_name

    return do_nothing() # needed as a fake callback, otherwise it throws errors