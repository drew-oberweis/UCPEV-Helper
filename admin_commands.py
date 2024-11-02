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

logger = logging.getLogger(__name__)

def confirm_admin(func):
    def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not utils.is_admin(update.effective_chat, update.effective_user, context):
            logger.info(f"Unauthorized access to command {func.__name__} by user {update.effective_user.id}")
            context.bot.send_message(update, context, "You are not authorized to use this command.")
            return
        return func(update, context)
    return wrapper


@confirm_admin
async def test_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Test admin command called")
    await context.bot.send_message(update.effective_chat.id, "You are an admin.")
    return