import logging
import time
import os
from dotenv import load_dotenv

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
import data

commands_descriptions = data.commands_descriptions

deployment = "DEV" # Change to "PROD" when deploying to production

prog_start_time = time.time()
log_filename = f"./logs/Log-{time.strftime('%Y-%m-%d-%H-%M-%S')}.log"
log_format = "%(asctime)s,%(name)s,%(levelname)s,%(message)s" # Logs readable as CSV because I am special

load_dotenv()

if deployment == "DEV":
    log_level = logging.DEBUG
    # token = os.environ["TELEGRAM_DEV_TOKEN"]
    token = os.getenv("telegram_dev")
else:
    log_level = logging.INFO
    # token = os.environ["TELEGRAM_PROD_TOKEN"]
    token = os.getenv("telegram_prod")

# set higher logging level for httpx to avoid all GET and POST requests being logged
# idk what this does but the example used it and it works so I'm keeping it
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore.http11").setLevel(logging.WARNING)
logging.getLogger("telegram.ext.ExtBot").setLevel(logging.WARNING)

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

def main():
    app = Application.builder().token(token).build()
    for i in commands: # Added programatically to make commands able to be referenced
        app.add_handler(CommandHandler(i, commands[i]))

    # make commands show when you type "/" in chat

    app.run_polling(allowed_updates=Update.ALL_TYPES)

main()