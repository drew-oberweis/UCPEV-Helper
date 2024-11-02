import os
import sys
from dotenv import load_dotenv 
import db

def get_env_vars():
    load_dotenv()
    try:
        token = os.environ["telegram_token"]
        deployment = "prod"
        db_creds = db.DB_Credentials(
            host=os.environ["postgres_host"],
            user=os.environ["postgres_user"],
            password=os.environ["postgres_pass"],
            database=os.environ["postgres_db"]
        )
    except KeyError: # If the token isn't found, it's a production deployment
        token = os.getenv("telegram_dev")
        deployment = "dev"
        db_creds = db.DB_Credentials(
            host=os.getenv("postgres_host"),
            user=os.getenv("postgres_user"),
            password=os.getenv("postgres_pass"),
            database=os.getenv("postgres_db")
        )
    return deployment, token, db_creds

def get_discord_webhook():
    load_dotenv()
    return os.getenv("discord_webhook")