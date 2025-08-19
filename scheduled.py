import logging
from utils import blind_send_message
import environment_handler

from telegram import (
    Update,
    User,
    Chat,
    ChatMember,
    ChatMemberUpdated,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
)

from telegram.constants import (
    ParseMode,
)

logger = logging.getLogger(__name__)

global tracked_locations
tracked_locations = []

async def do_nothing():
    return

async def check_queue(context: ContextTypes.DEFAULT_TYPE):
    """Check the queue for messages to forward."""

    q = context.job.data

    messages = q.get_queue("telegram")

    telegram_main_id = environment_handler.get_telegram_chat_id()

    if messages:
        for message in messages:
            output = f"{message.get_user()}: {message.get_message()}"
            result = await blind_send_message(
                chat_id=telegram_main_id,
                message=output,
                topic_id=message.get_telegram_topic_id(),
                context=context,
            )
            if not result:
                logger.debug(f"Failed to forward message to Telegram: {output} from {message.get_user()} in chat {message.get_chat()} with ID {message.get_telegram_topic_id()}")
            else:
                logger.debug(f"Forwarded message to Telegram: {output} from {message.get_user()} in chat {message.get_chat()} with ID {message.get_telegram_topic_id()}")
    else:
        # logger.debug("No messages to forward to Telegram in the queue.")
        None

    def do_nothing():
        return None

    return do_nothing() # this is so stupid