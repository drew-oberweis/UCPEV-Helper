import os
import logging
import yaml

logger = logging.getLogger(__name__)

def read_config(file_path: str = "./config/config.yml") -> dict:
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
            logger.info(f"Configuration loaded successfully from {file_path}")
            return config
    except Exception as e:
        logger.error(f"Error loading configuration from {file_path}: {e}")
        return {}

def get_telegram_token():
    config = read_config()
    try:
        token = config['telegram_token']
    except KeyError:
        logger.error("Telegram token not found in configuration.")
        token = None
    return token

def get_discord_token():
    config = read_config()
    try:
        token = config['discord_token']
    except KeyError:
        logger.error("Discord token not found in configuration.")
        token = None
    return token

def get_discord_announcement_webhook() -> str:
    config = read_config()
    try:
        webhook = config['discord_announcement_webhook']
    except KeyError:
        logger.error("Discord announcement webhook not found in configuration.")
        webhook = None
    return webhook

def get_discord_webhook(channel: str) -> str:
    config = read_config()
    try:
        webhook = config[f"channel_{channel}"]
    except KeyError:
        logger.error(f"{channel} webhook not found in configuration.")
        webhook = None
    return webhook
    
def get_telegram_chat_id():
    config = read_config()
    try:
        chat_id = int(config['telegram_chat_id'])
    except KeyError:
        logger.error("Telegram chat ID not found in configuration.")
        chat_id = None
    except ValueError:
        logger.error("Telegram chat ID in configuration is not a valid integer.")
        chat_id = None

    return chat_id

def get_log_level():
    config = read_config()
    raw = config.get("log_level")

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
    config = read_config()
    try:
        name = config['database'].get('db_name')
        user = config['database'].get('db_user')
        password = config['database'].get('db_password')
        host = config['database'].get('db_host')
        port = config['database'].get('db_port')
    except KeyError as e:
        logger.error(f"Database configuration error: {e}")
        return None
    return name, user, password, host, port