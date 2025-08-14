import logging
import time
import os
import sys
import asyncio

from telegram import (
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
    filters,
    ConversationHandler
)

import user_commands
import admin_commands
import data
import environment_handler
import message_handler
import utils
import message_queue
from utils import UpdateBundle
import scheduled

logger = logging.getLogger(__name__)

token = environment_handler.get_telegram_token()

commands_map = {
    "nosedive": user_commands.nosedive,
    "rules": user_commands.rules,
    "links": user_commands.links,
    "codes": user_commands.codes,
    "helmet": user_commands.helmet,
    "help": user_commands.help,
    "pads": user_commands.pads,
    "i2s": user_commands.i2s,
    "rides": user_commands.rides,
    "econtact": user_commands.econtact,
}

admin_commands_map = {
    "test_admin": admin_commands.test_admin,
    "announce": admin_commands.announce,
    "make_ride_poll": admin_commands.make_ride_poll,
    "send_topic_id": admin_commands.send_topic_id,
}

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a message to the user."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    try:
        ub = UpdateBundle(update, context)
        await ub.send_message("An error occurred while processing your request. Please try again later.\n\nError message: " + str(context.error))
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

def main(queue=None):
    logger.info("Telgram bot start initiated")
    app = Application.builder().token(token).build()

    for i in commands_map:
        app.add_handler(CommandHandler(i, commands_map[i]))
    for i in admin_commands_map:
        app.add_handler(CommandHandler(i, admin_commands_map[i]))

    app.add_handler(ChatMemberHandler(user_commands.welcome, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.LOCATION, message_handler.location_message_handler))

    app.add_handler(MessageHandler(filters.ALL ,message_handler.on_message))

    # add loop to run ever n seconds to check the queue for messages to forward
    if queue is not None:
        logger.info("Setting up message queue checking...")
        app.job_queue.run_repeating(scheduled.check_queue, interval=1, first=0, data=queue)
    else:
        logger.warning("No message queue provided, this instance will not support message forwarding between platforms.")

    app.add_error_handler(error_handler)

    utils.output_telegram_autocomplete()

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

# logger.log(logging.CRITICAL, "How did we get here?")