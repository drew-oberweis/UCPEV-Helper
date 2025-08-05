import logging
import time
import os
import sys

from telegram import (
    Update,
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
from message_queue import Message

logger = logging.getLogger(__name__)
token = environment_handler.get_telegram_token()

def do_nothing():
    return None

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    ub = utils.UpdateBundle(update, context)

    topic_id = ub.update.message.message_thread_id

    if topic_id == None:
        topic_id = 0

    user = ub.get_user()
    username = user.username

    # ignore if private chat
    if(ub.get_chat().type == "private"):
        return do_nothing()

    # ignore bot's own messages
    if(user.is_bot):
        return do_nothing()
    if(update.effective_user.id == context.bot.id):
        return do_nothing()

    if(username == None):
        try:
            username = user.first_name + " " + user.last_name
        except:
            username = user.first_name

    logger.debug(f"Received message from {username} ({user.id}) in chat {topic_id}: {update.effective_message.text}")
    
    # send message to discord using the correct webhook
    
    message = Message()
    message.set_dest_platform("discord")
    message.set_user(username)
    message.set_message(update.effective_message.text)
    message.set_chat_id("discord", topic_id)

    webhook = message.get_discord_webhook()

    if webhook:
        utils.send_discord_webhook(webhook, update.effective_message.text, False, username)
    else:
        logger.error(f"No webhook found for channel {message.get_chat_id()}. Cannot send message to Discord.")

    return do_nothing() # needed as a fake callback, otherwise it throws errors