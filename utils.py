import logging
from typing import Optional
import os
import zipfile
import shutil

from telegram import (
    Update,
    User,
    Chat,
    ChatMember,
    ChatMemberUpdated,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
)

from telegram.constants import (
    ParseMode,
)

import db
from discord_webhook import DiscordWebhook
import data
import YoursTruly
import environment_handler

token, db_creds = environment_handler.get_env_vars()

logger = logging.getLogger(__name__)

async def is_admin(user: User):

    db_creds = db.DB_Credentials(
        host=os.getenv("postgres_host", None),
        user=os.getenv("postgres_user", None),
        password=os.getenv("postgres_pass", None),
        database=os.getenv("postgres_db", None)
    )

    session = db.Session(db_creds)

    db_user = session.get_user(user.id)

    if not db_user:
        logger.log(logging.INFO, f"User {user.id} does not exist in the database")
        return False

    status = db_user[2]

    if status == "True":
        status = True
    else:
        status = False

    logger.log(logging.INFO, f"User {user.id} is{' not' if not status else ''} an admin")
    return status


# This is a direct rip from https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/chatmemberbot.py
def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member

def send_discord_webhook(url: str, message: str, ping_all: bool = False):
    if ping_all:
        message = "@everyone " + message
    webhook = DiscordWebhook(url=url, content=message, username="UC PEV Helper")
    response = webhook.execute()
    return response

def output_telegram_autocomplete():
    output = ""

    for i in data.command_descriptions:
        output += f"{i} - {data.command_descriptions[i]}\n"

    for i in data.admin_command_descriptions:
        output += f"{i} - {data.admin_command_descriptions[i]} (Admin only)\n"

    logger.log(logging.INFO, f"\nThe following output was generated to update the autocomplete list: \n\n{output}-----------------------\nIt has also been saved to commands.txt\n")
    return output

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    # logger.debug(f"Sending message: {message}")
    # reply to the message that called this command
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)
    return

async def download_ride(context, file_id, file_name, user_id):

    # make sure directory exists
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    file = await context.bot.get_file(file_id)
    logger.log(logging.DEBUG, f"Downloading ride {file_id} to {file_name}")
    await file.download_to_drive("./downloads/ride.zip")
    logger.log(logging.DEBUG, f"Downloaded ride {file_id} to {file_name}")

    # extract the zip file
    with zipfile.ZipFile("./downloads/ride.zip", 'r') as zip_ref:
        zip_ref.extractall(f"./downloads/{file_name}")
    
    logger.log(logging.DEBUG, f"Extracted ride {file_id} to {file_name}")

    # delete the zip file
    os.remove("./downloads/ride.zip")
    logger.log(logging.DEBUG, f"Deleted ride zip folder")

    ride = YoursTruly.Ride(f"./downloads/{file_name}/YT_ride.json")

    # verify that rides folder exists
    if not os.path.exists("rides"):
        os.makedirs("rides")

    # move json to rides folder, and rename it to the ride ID
    shutil.move(f"./downloads/{file_name}/YT_ride.json", f"./rides/{ride.getId()}.json")

    # clean up downloads folder
    os.rmdir(f"./downloads/{file_name}")

    session = db.Session(db_creds)

    session.write_ride_upload(ride.getId(), user_id)

    return ride