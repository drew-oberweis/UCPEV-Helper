import logging
from datetime import datetime

from telegram import (
    Update,
)
from telegram.ext import (
    ContextTypes,
)

import data
import environment_handler
import utils
from message_queue import Message
from location import LocPoint
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
    
    announcement_topic = data.announcement_topic_dev if environment_handler.get_log_level() == logging.DEBUG else data.announcement_topic_prod
    if update.effective_message.message_thread_id == announcement_topic:
        is_admin = await utils.is_admin(update, context)
        if is_admin:
            pass
        else:
            # delete message as user is not an admin
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.id)
            logger.info(f"User {username} tried to send a message to the announcement channel {announcement_topic} but is not an admin. Message deleted.")
            return

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
        timestamp=datetime.now().timestamp(), # use current time
    )

    # Set user and timestamp
    loc_point.set_user(ub.get_user().username)
    loc_point.set_heading(loc_obj.heading if hasattr(loc_obj, 'heading') else None)

    # Insert location point into the database

    session = db.Session()

    session.insert_location_point(
        latitude=loc_point.get_lat(),
        longitude=loc_point.get_lon(),
        user_id=ub.get_user().id,
        timestamp=loc_point.get_timestamp(),
        heading=loc_point.get_heading(),
        source_message_id=update.effective_message.message_id
    )

    return do_nothing()