import logging

from telegram import (
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
)
from telegram.constants import ParseMode
import data
import utils
import environment_handler

logger = logging.getLogger(__name__)
token, db_creds = environment_handler.get_env_vars()

def confirm_admin(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        is_admin = await utils.is_admin(update.effective_chat, update.effective_user, context)
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

    return