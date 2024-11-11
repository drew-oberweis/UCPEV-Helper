import os
import sys
from dotenv import load_dotenv 
import db
import logging

logger = logging.getLogger(__name__)

def get_env_vars():
    load_dotenv()
    token = os.environ['telegram_token']
    try:
        db_creds = db.DB_Credentials(
            host=os.environ["postgres_host"],
            user=os.environ["postgres_user"],
            password=os.environ["postgres_pass"],
            database=os.environ["postgres_db"]
        )
    except KeyError:
        logger.error("Database credentials not found in environment variables.")
        db_creds = None
    return token, db_creds

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
        return logging.INFO # info should be default