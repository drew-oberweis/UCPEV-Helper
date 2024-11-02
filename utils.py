import logging

from telegram import (
    Update,
    User,
    Chat
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
)

logger = logging.getLogger(__name__)

async def is_admin(chat: Chat, user: User, context: ContextTypes.DEFAULT_TYPE):
    admins = await context.bot.get_chat_administrators(chat.id)
    status = user.id in [admin.user.id for admin in admins]
    logger.log(logging.INFO, f"User {user.id} is{' not' if not status else ''} an admin in chat {chat.id}")