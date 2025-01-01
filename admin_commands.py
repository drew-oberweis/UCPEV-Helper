import logging
from datetime import datetime

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters
)
from telegram.constants import ParseMode
import data
import utils
import environment_handler
import db

logger = logging.getLogger(__name__)
token, db_creds = environment_handler.get_env_vars()

def confirm_admin(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        is_admin = await utils.is_admin(update.effective_user)
        if not is_admin:
            logger.info(f"Unauthorized access to command {func.__name__} by user {update.effective_user.id}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You are not authorized to use this command.")
            return
        return await func(update, context)
    return wrapper


@confirm_admin
async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Test admin command called")
    await context.bot.send_message(update.effective_chat.id, "You are an admin.")
    return

@confirm_admin
async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(context.args) == 0:
        await context.bot.send_message(update.effective_chat.id, "Please provide a message to announce.")
        return
    message = " ".join(context.args)
    message = await context.bot.send_message(update.effective_chat.id, message)

    await message.pin()

    webhook_url = environment_handler.get_discord_webhook()
    utils.send_discord_webhook(webhook_url, message.text, True)

    await context.bot.delete_message(update.effective_chat.id, update.message.message_id)

@confirm_admin
async def make_ride_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        selected_id = context.args[0]
    except IndexError:
        selected_id = None
    
    session = db.Session(db_creds)
    ride = session.get_ride(selected_id)

    if not ride:
        await context.bot.send_message(update.effective_chat.id, "Ride not found.")
        return
    
    """
    Default poll:
        Be there
        Be square
        Maybe

    If pace is "both":
        Be there (fast)
        Be there (slow)
        Be there (both)
        Be square
        Maybe
    """

    # generate poll expiration, midnight of the day of the ride
    poll_expiration = ride.date + 86400
    poll_expiration_datetime = datetime.fromtimestamp(poll_expiration)

    # Delete the command message
    await context.bot.delete_message(update.effective_chat.id, update.message.message_id)

    # Send ride info message
    message = f"Ride info:\n{ride}"
    await context.bot.send_message(update.effective_chat.id, message)

    # generate poll options
    poll_options = ["Be there", "Be square", "Maybe"]
    if ride.pace == "Both (Separate rides)":
        poll_options = ["Be there (fast)", "Be there (slow)", "Be there (both)", "Be square", "Maybe"]

    poll_message = " ^^ Will you be at this ride? ^^"

    # send poll
    poll = await context.bot.send_poll(update.effective_chat.id, question=poll_message, options=poll_options, is_anonymous=False, allows_multiple_answers=False)