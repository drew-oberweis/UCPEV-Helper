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
import custom_handlers as c_handlers
import utils
from utils import UpdateBundle

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
}

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a message to the user."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    ub = UpdateBundle(update, context)
    await ub.send_message("An error occurred while processing your request. Please try again later.\n\nError message: " + str(context.error))

def main():
    logger.info("Telgram bot start initiated")
    app = Application.builder().token(token).build()

    for i in commands_map:
        app.add_handler(CommandHandler(i, commands_map[i]))
    for i in admin_commands_map:
        app.add_handler(CommandHandler(i, admin_commands_map[i]))

    app.add_handler(ChatMemberHandler(user_commands.welcome, ChatMemberHandler.CHAT_MEMBER))
    # app.add_handler(MessageHandler(filters.ALL ,c_handlers.on_message))

    app.add_error_handler(error_handler)

    command_list = utils.output_telegram_autocomplete()
    # write the command list to a file
    with open("commands.txt", "w") as f:
        f.write(command_list)

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

# logger.log(logging.CRITICAL, "How did we get here?")