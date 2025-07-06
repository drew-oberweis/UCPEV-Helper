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
        is_admin = await utils.is_admin(ub.update, ub.context)
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

    try:
        ride_inf = shit.get_rides()[0]
    except IndexError as e:
        await ub.send_message("There are no rides scheduled")
        return

    organizer = ride_inf[0]
    name = ride_inf[1]
    date = ride_inf[2]
    time = ride_inf[3]
    route = ride_inf[4]
    pace = ride_inf[5]
    extra = ride_inf[6]

    route_inf = shit.get_route(route)

    start_loc = route_inf[1]
    start_pin = route_inf[2]
    notable_loc = route_inf[3]
    end_loc = route_inf[4]
    end_pin = route_inf[5]
    dist = route_inf[6]
    gaia_link = route_inf[7]
    route_desc = route_inf[8]
    route_extra = route_inf[9]

    if extra != "":
        extra = f"\n\n{extra}"

    ride_message = f"{name}\nOrganizer: {organizer}\n\nDate/Time: {date} @ {time}\nPace: {pace}{extra}"
    
    if start_pin == "":
        start_msg = f"Start Location: {start_loc}"
    else:
        start_msg = f"Start Location: {start_loc} ({start_pin})"

    if end_pin == "":
        end_msg = f"End Location: {end_loc}"
    else:
        end_msg = f"End Location: {end_loc} ({end_pin})"

    route_message = f"Route Name: {route}\n{start_msg}\n{end_msg}\nPOI: {notable_loc}\nDistance: {dist} miles\nGAIA Link: {gaia_link}\n\nRoute Description: {route_desc}\n\n{route_extra}"

    message = ride_message + "\n\n" + route_message
    
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
    ride_date_timestamp = datetime.strptime(date, "%m/%d/%Y").timestamp()
    poll_expiration = ride_date_timestamp + 86400

    # Delete the command message
    await context.bot.delete_message(update.effective_chat.id, update.message.message_id) #TODO: implement this using UpdateBundle

    # Send ride info message
    await ub.send_message(message)

    # generate poll options
    poll_options = ["Be there", "Be square", "Maybe"]
    poll_message = " ^^ Will you be at this ride? ^^"

    # send poll
    await context.bot.send_poll(update.effective_chat.id, question=poll_message, options=poll_options, is_anonymous=False, allows_multiple_answers=False, message_thread_id=update.effective_message.message_thread_id)

    webhook_url = environment_handler.get_discord_webhook()
    utils.send_discord_webhook(webhook_url, "Ride poll posted in Telegram! Head over there to check it out!", True)