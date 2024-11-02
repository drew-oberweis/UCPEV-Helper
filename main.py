import logging
import time
import os
import sys
from dotenv import load_dotenv

from telegram import (
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
)

import simple_commands
import admin_commands
import data

commands_descriptions = data.commands_descriptions

prog_start_time = time.time()
log_filename = f"./logs/Log-{time.strftime('%Y-%m-%d-%H-%M-%S')}.log"
log_format = "%(asctime)s,%(name)s,%(levelname)s,%(message)s" # Logs readable as CSV because I am special

# set higher logging level for httpx to avoid all GET and POST requests being logged
# idk what this does but the example used it and it works so I'm keeping it
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore.http11").setLevel(logging.WARNING)
logging.getLogger("telegram.ext.ExtBot").setLevel(logging.WARNING)



logger = logging.getLogger(__name__)


load_dotenv()

try:
    log_level = logging.INFO
    token = os.environ["telegram_token"]
    # token = os.getenv("telegram_token")
    logging.basicConfig(format=log_format, level=logging.INFO, stream=sys.stdout)
    logger.log(logging.INFO, "Production deployment detected, using production token and log config")
except KeyError: # If the token isn't found, it's a production deployment
    # token = os.environ["TELEGRAM_DEV_TOKEN"]
    token = os.getenv("telegram_dev")
    logging.basicConfig(format=log_format, level=logging.DEBUG, filename=log_filename)
    logger.log(logging.INFO, "Development deployment detected, using development token and log config")


commands = {
    "nosedive": simple_commands.nosedive,
    "rules": simple_commands.rules,
    "links": simple_commands.links,
    "codes": simple_commands.codes,
    "helmet": simple_commands.helmet,
    "help": simple_commands.help,
    "pads": simple_commands.pads
}

admin_commands = {
    "test_admin": admin_commands.test_admin
}

def main():
    app = Application.builder().token(token).build()
    for i in commands: # Added programatically to make commands able to be referenced
        app.add_handler(CommandHandler(i, commands[i]))
    for i in admin_commands:
        app.add_handler(CommandHandler(i, admin_commands[i]))

    app.add_handler(ChatMemberHandler(simple_commands.welcome, ChatMemberHandler.CHAT_MEMBER))

    # TODO: make commands show when you type "/" in chat

    app.run_polling(allowed_updates=Update.ALL_TYPES)

main()