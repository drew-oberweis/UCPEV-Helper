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

def get_discord_token():
    load_dotenv()
    try:
        token = os.environ['discord_token']
    except KeyError:
        logger.error("Discord token not found in environment variables.")
        token = None
    return token

def get_discord_webhook(channel: str) -> str:
    load_dotenv()

    try:
        env_name = f"{channel}_webhook"
        webhook = os.environ[env_name]
        logger.debug(f"Found {webhook} while searching for {env_name} in environment variables.")
        if not webhook:
            raise ValueError(f"Webhook for {channel} is not set in environment variables when searching for {env_name}.")
        return webhook
    except KeyError:
        logger.error(f"{channel} webhook not found in environment variables when searching for {env_name}.")
        return None
    
def get_telegram_chat_id():
    load_dotenv()
    try:
        chat_id = int(os.environ['telegram_chat_id'])
    except KeyError:
        logger.error("Telegram chat ID not found in environment variables.")
        chat_id = None
    except ValueError:
        logger.error("Telegram chat ID in environment variables is not a valid integer.")
        chat_id = None

    return chat_id

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

def get_database_config():
    load_dotenv()
    try:
        name = os.environ['db_name']
        user = os.environ['db_user']
        password = os.environ['db_password']
        host = os.environ['db_host']
        port = os.environ['db_port']
        database = os.environ['db_database']
    except KeyError as e:
        logger.error(f"Database configuration error: {e}")
        return None
    return name, user, password, host, port, database