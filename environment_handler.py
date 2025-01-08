import os
import sys
from dotenv import load_dotenv 
import db
import logging

logger = logging.getLogger(__name__)

def get_env_vars():
    load_dotenv()
    try:
        token = os.environ['telegram_token']
    except KeyError:
        logger.error("Telegram token not found in environment variables.")
        token = None
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
        logger.warning("Invalid log level or no log level present in environment variables. Defaulting to INFO.")
        return logging.INFO # info should be default
    
def generate_google_creds():
    logger.info("Pulling Google credentials...")
    # Load environment variables and store them into the correct files
    load_dotenv()

    creds = os.getenv("GOOGLE_CREDS_FILE")
    token = os.getenv("GOOGLE_TOKEN_FILE")

    if creds is None or token is None:
        logger.error("Google credentials or token not found in environment variables.")
        return None, None
    
    with open("google_creds.json", "w") as f:
        f.write(creds)
    with open("google_token.json", "w") as f:
        f.write(token)

    logger.info("Google credentials pulled.")

    return "google_creds.json", "google_token.json"
