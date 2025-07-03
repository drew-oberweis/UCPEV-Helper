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
from utils import UpdateBundle
import sheets_interface as shit
from ride import Ride

logger = logging.getLogger(__name__)
token, db_creds = environment_handler.get_env_vars()

def confirm_admin(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        ub = UpdateBundle(update, context)
        is_admin = await utils.is_admin(update.effective_user)
        if not is_admin:
            logger.info(f"Unauthorized access to command {func.__name__} by user {update.effective_user.id}")
            await ub.send_message("You are not authorized to use this command.")
            return
        return await func(update, context)
    return wrapper


@confirm_admin
async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Test admin command called")
    ub = UpdateBundle(update, context)
    await ub.send_message("You are an admin.")
    return

@confirm_admin
async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    ub = UpdateBundle(update, context)
    if len(context.args) == 0:
        await ub.send_message("Please provide a message to announce.")
        return
    message = f"Announcement from {ub.update.effective_user}:\n\n".join(context.args)
    message = await ub.send_message(message)

    await message.pin()

    webhook_url = environment_handler.get_discord_webhook()
    utils.send_discord_webhook(webhook_url, message.text, True)

    await context.bot.delete_message(update.effective_chat.id, update.message.message_id)

@confirm_admin
async def make_ride_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):

    ub = UpdateBundle(update, context)

    ride_inf = shit.get_rides()[0]

    ride = Ride()

    ride.set_organizer(ride_inf[0])
    ride.set_name(ride_inf[1])
    ride.set_date(ride_inf[2])
    ride.set_time(ride_inf[3])
    ride.set_route(ride_inf[4])
    ride.set_pace(ride_inf[5])
    ride.set_description(ride_inf[6])

    if not ride:
        await ub.send_message("Ride not found.")
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
    await context.bot.delete_message(update.effective_chat.id, update.message.message_id) #TODO: implement this using UpdateBundle

    # Send ride info message
    message = f"Ride info:\n{ride}"
    await ub.send_message(message)

    # generate poll options
    poll_options = ["Be there", "Be square", "Maybe"]
    if ride.pace == "Both (Separate rides)":
        poll_options = ["Be there (fast)", "Be there (slow)", "Be there (both)", "Be square", "Maybe"]

    poll_message = " ^^ Will you be at this ride? ^^"

    # send poll
    poll = await context.bot.send_poll(update.effective_chat.id, question=poll_message, options=poll_options, is_anonymous=False, allows_multiple_answers=False)