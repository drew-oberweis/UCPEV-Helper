import logging
from datetime import datetime

from telegram import (
    Update,
)
from telegram.ext import (
    ContextTypes,
)
from telegram.constants import ParseMode
import utils
import environment_handler
from utils import UpdateBundle
import sheets_interface as shit

logger = logging.getLogger(__name__)
token = environment_handler.get_telegram_token()

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
    message = f"Announcement from {ub.update.effective_user}:\n\n".join(args)
    message = await ub.send_message(message)

    await message.pin()

    webhook_url = environment_handler.get_discord_webhook()
    utils.send_discord_webhook(webhook_url, message.text, True)

    await context.bot.delete_message(update.effective_chat.id, update.message.message_id)

@confirm_admin
async def send_topic_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ub = UpdateBundle(update, context)
    topic_id = ub.get_message().message_thread_id
    await ub.send_message(f"Topic ID: {topic_id}")

@confirm_admin
async def make_ride_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):

    ub = UpdateBundle(update, context)

    try:
        ride = shit.get_upcoming_rides()[0]
    except IndexError as e:
        await ub.send_message("There are no rides scheduled")
        return

    message = utils.generate_ride_text(ride)

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

    # generate poll expiration, 36 hours after message sent
    poll_expiration = datetime.now().timestamp() + 129600

    # Delete the command message
    await context.bot.delete_message(update.effective_chat.id, update.message.message_id) #TODO: implement this using UpdateBundle

    # Send ride info message
    await ub.send_message(message)

    # generate poll options
    poll_options = ["Be there", "Be square", "Maybe"]
    poll_message = " ^^ Will you be at this ride? ^^"

    # send poll
    await context.bot.send_poll(update.effective_chat.id, question=poll_message, options=poll_options, is_anonymous=False, allows_multiple_answers=False, message_thread_id=update.effective_message.message_thread_id)

    webhook_url = environment_handler.get_discord_announcement_webhook()
    utils.send_discord_webhook(webhook_url, "Ride poll posted in Telegram! Head over there to check it out!", True)