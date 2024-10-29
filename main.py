import logging
import time
import os

from telegram import (
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
)

import simple_commands

deployment = "DEV" # Change to "PROD" when deploying to production

prog_start_time = time.time()
log_filename = f"./logs/Log-{time.strftime('%Y-%m-%d-%H-%M-%S')}.log"
log_format = "%(asctime)s,%(name)s,%(levelname)s,%(message)s" # Logs readable as CSV because I am special

if deployment == "DEV":
    log_level = logging.DEBUG
    token = "7576351329:AAH-_giC8C3IpOz5cXNaaf5YIPx3hpu9j6c" # Hardcoded tokens LETS GOOOOOOOOO
else:
    log_level = logging.INFO
    token = os.getenv("TOKEN") # See I do some things right

# set higher logging level for httpx to avoid all GET and POST requests being logged
# idk what this does but the example used it and it works so I'm keeping it
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore.http11").setLevel(logging.WARNING)

logging.basicConfig(format=log_format, level=log_level, filename=log_filename)

logger = logging.getLogger(__name__)

commands = {
    "nosedive": simple_commands.nosedive,
    "rules": simple_commands.rules,
    "links": simple_commands.links,
    "codes": simple_commands.codes,
    "helmet": simple_commands.helmet,
    "help": simple_commands.help,
    "pads": simple_commands.pads
}

commands_descriptions = {
    "nosedive": "Sends a link to a nosedive video",
    "rules": "Sends the rules of the group",
    "links": "Sends a list of useful links",
    "codes": "Sends a link to a list of discount codes",
    "helmet": "Sends a list of recommended helmet brands",
    "help": "Sends a list of commands",
    "pads": "Sends a list of recommended pads"
}



def main():
    app = Application.builder().token(token).build()
    for i in commands: # Added programatically to make commands able to be referenced
        app.add_handler(CommandHandler(i, commands[i]))

    # make commands show when you type "/" in chat

    app.run_polling(allowed_updates=Update.ALL_TYPES)

main()