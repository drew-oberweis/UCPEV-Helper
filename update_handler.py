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

import data
import environment_handler
import utils
from message_queue import Message
from location import LocPoint
import scheduled
import db

logger = logging.getLogger(__name__)
token = environment_handler.get_telegram_token()

def do_nothing():
    return None

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    ub = utils.UpdateBundle(update, context)

    try:
        topic_id = ub.update.message.message_thread_id
    except AttributeError:
        return do_nothing()

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

    msg_text = update.effective_message.text
    logger.debug(f"Message text: [{msg_text}]")

    if msg_text == "" or msg_text == None:
        # check caption for text, it is put there if message is a photo
        logger.debug(f"No text found in message, using caption: {update.effective_message.caption}")
        msg_text = update.effective_message.caption

    logger.debug(f"Message text after caption check: [{msg_text}]")

    if msg_text == None or msg_text == "":
        logger.debug("No message text found, skipping sending to Discord.")
        return do_nothing()

    message = Message() # build into object for validation
    message.set_user(username)
    message.set_message(msg_text)
    message.set_telegram_topic_id(topic_id)

    webhook = message.get_discord_webhook()

    if webhook:
        utils.send_discord_webhook(webhook, message.get_message(), False, message.get_user())
    else:
        logger.error(f"No webhook found for channel {message.get_telegram_topic_id()}. Cannot send message to Discord.")

    return do_nothing() # needed as a fake callback, otherwise it throws errors

async def location_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ub = utils.UpdateBundle(update, context)
    loc_obj = update.effective_message.location

    # check if location is a live location, just a one-off. Ignore if one-off
    if not loc_obj.live_period:
        logger.debug("Received a one-off location, ignoring.")
        return do_nothing()

    logger.debug(f"Received location: {loc_obj}")

    # Create a new location point object
    loc_point = LocPoint(
        latitude=loc_obj.latitude,
        longitude=loc_obj.longitude,
        timestamp=loc_obj.timestamp
    )

    # Set user and timestamp
    loc_point.set_user(ub.get_user().username)

    # Insert location point into the database
    db.insert_location_point(
        latitude=loc_point.get_lat(),
        longitude=loc_point.get_lon(),
        speed=loc_point.get_speed(),
        user_id=loc_point.get_user(),
        timestamp=loc_point.get_timestamp()
    )

    return do_nothing()