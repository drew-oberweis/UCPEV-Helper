import os
import sys
from dotenv import load_dotenv 
import logging

logger = logging.getLogger(__name__)

def get_telegram_token():
    load_dotenv()
    try:
        token = os.environ['telegram_token']
    except KeyError:
        logger.error("Telegram token not found in environment variables.")
        token = None
    return token

def get_discord_webhook():
    load_dotenv()
    return os.getenv("discord_webhook")

def get_log_level():
    load_dotenv()
    raw =  os.getenv("log_level")

    if raw == "DEBUG":
        return logging.DEBUG
    elif raw == "INFO":
        return logging.INFO
    elif raw == "WARNING":
        return logging.WARNING
    elif raw == "ERROR":
        return logging.ERROR
    elif raw == "CRITICAL":
        return logging.CRITICAL
    else:
        logger.warning("Invalid log level or no log level present in environment variables. Defaulting to INFO.")
        return logging.INFO # info should be default
