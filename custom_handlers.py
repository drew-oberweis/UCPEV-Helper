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

import simple_commands
import admin_commands
import data
import db
import environment_handler
import utils

logger = logging.getLogger(__name__)
token, db_creds = environment_handler.get_env_vars()

def do_nothing():
    return None

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # ignore if private chat
    if(update.effective_chat.type == "private"):
        return do_nothing()
    
    is_admin = await is_telegram_admin(update, context)

    session = db.Session(db_creds)
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message
    chat_id = chat.id
    user_id = user.id
    username = user.username
    content = message.text

    if(username == None):
        username = user.first_name + " " + user.last_name

    session.add_message(message.message_id, user_id, chat_id, content)

    stored_user = session.get_user(user_id=user_id)
    if(stored_user is None):
        session.add_user(username, user_id, is_admin)
        return do_nothing()

    if(stored_user[0] != username or stored_user[2] != is_admin): # update user if username or admin status has changed
        session.update_user(user_id, username, is_admin)


    return do_nothing() # needed as a fake callback, otherwise it throws errors

async def is_telegram_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if(update.effective_chat.type == "private"):
        return False

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    is_admin = False

    try:
        chat_admins = await context.bot.get_chat_administrators(chat_id)
        
        for admin in chat_admins:
            if(admin.user.id == user_id):
                return True
    except Exception as e:
        logger.error(f"Error getting chat admins: {e}")
        return False
    return is_admin