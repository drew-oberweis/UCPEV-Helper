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

logging.basicConfig(format=log_format, level=log_level, filename=log_filename)

logger = logging.getLogger(__name__)


def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Test command called")
    print("Test command called")
    return "Test command called"


def main():
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("nosedive", simple_commands.nosedive))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

main()