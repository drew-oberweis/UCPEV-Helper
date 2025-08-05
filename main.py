import threading
import logging
import time
import sys

import telegram_main
import discord_main
import environment_handler

log_filename = f"./logs/Log-{time.strftime('%Y-%m-%d-%H-%M-%S')}.log"
log_format = "%(asctime)s,%(name)s,%(levelname)s,%(message)s" # Logs readable as CSV because I am special

# set higher logging level for httpx to avoid all GET and POST requests being logged

extraLogLevel = logging.WARNING

logging.getLogger("httpx").setLevel(extraLogLevel)
logging.getLogger("httpcore.http11").setLevel(extraLogLevel)
logging.getLogger("telegram.ext.ExtBot").setLevel(extraLogLevel)
logging.getLogger("telegram.ext.Application").setLevel(extraLogLevel)
logging.getLogger("httpcore.connection").setLevel(extraLogLevel)
logging.getLogger("telegram.ext.Updater").setLevel(extraLogLevel)
logging.getLogger("telegram.ext.ConversationHandler").setLevel(extraLogLevel)

log_level = environment_handler.get_log_level()
logging.basicConfig(format=log_format, level=log_level, stream=sys.stdout, force=True)

logger = logging.getLogger(__name__)

logger.info("Logging initialized.")

def launch_bots():
    logger.info("Starting Discord bot in separate thread...")
    discord_thread = threading.Thread(target=discord_main.main)
    discord_thread.start()
    logger.info("Discord bot started.")

    telegram_main.main() # call the function to hand the main thread to the Telegram bot

    logger.CRITICAL("Telegram bot has stopped running. Exiting program.")

logger.info("Beginning bot startup...")

launch_bots()