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
    UserProfilePhotos
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

from discord_webhook import DiscordWebhook
import data
import environment_handler
from data import chat_id_map
from ride import Ride
import sheets_interface as shit

token = environment_handler.get_telegram_token()

logger = logging.getLogger(__name__)

class UpdateBundle:
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.update = update
        self.context = context

    def get_update(self) -> Update:
        return self.update
    
    def get_context(self) -> ContextTypes.DEFAULT_TYPE:
        return self.context
    
    def get_chat(self) -> Chat:
        return self.update.effective_chat
    
    def get_user(self) -> User:
        return self.update.effective_user
    
    def get_message(self) -> Optional[str]:
        return self.update.effective_message
    
    def get_text(self) -> Optional[str]:
        return self.update.effective_message.text
    
    async def send_message(self, message: str):
        # logger.debug(f"Sending message: {message}")
        # reply to the message that called this command
        try:
            context = self.get_context()
            update = self.get_update()
            logger.log(logging.DEBUG, f"Chat ID: {update.effective_chat.id}")
            message = await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML, message_thread_id=update.effective_message.message_thread_id)
            return message
        except Exception as e:
            message = await context.bot.send_message(chat_id=update.effective_chat.id, text="Error: " + str(e), parse_mode=ParseMode.HTML, message_thread_id=update.effective_message.message_thread_id)
            return message
    
    async def send_reply(self, message: str):
        return await self.update.effective_message.reply_text(message)

async def blind_send_message(chat_id: int, message: str, topic_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:

    if(topic_id == None):
        return False

    """Send a message to a chat without any context."""
    try:
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML, message_thread_id=topic_id)
    except Exception as e:
        raise Exception(f"Failed to send message to chat {chat_id}: {e}")
    return True
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

def send_discord_webhook(url: str, message: str, ping_all: bool = False, username: str = "UC PEV Helper", avatar_url: str = None) -> None:
    if ping_all:
        message = "@everyone " + message
    webhook = DiscordWebhook(url=url, content=message, username=username, avatar_url=avatar_url)
    response = webhook.execute()
    return response

def output_telegram_autocomplete():

    output = ""

    for i in data.command_descriptions:
        output += f"{i} - {data.command_descriptions[i]}\n"

    for i in data.admin_command_descriptions:
        output += f"{i} - {data.admin_command_descriptions[i]} (Admin only)\n"

    with open("commands.txt", "w") as f:
        f.write(output)

    logger.log(logging.INFO, f"\nThe following output was generated to update the autocomplete list: \n\n{output}-----------------------\nIt has also been saved to commands.txt\n")
    return output

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE): # can't be UpdateBundle because it needs to match the default params of TPB callbacks
    if(update.effective_chat.type == "private"):
        return False

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    is_admin = False

    try:
        chat_admins = await context.bot.get_chat_administrators(chat_id)
        
        for admin in chat_admins:
            if(admin.user.id == user_id):
                return True
    except Exception as e:
        logger.error(f"Error getting chat admins: {e}")
        return False
    return is_admin

def generate_ride_text(ride: Ride) -> str:
    # get the route of the selected ride
    route = shit.get_route(ride.route)
    if not route:
        return "Route not found"

    logger.debug(route)

    extra = ride.description # pulled to enable cleaning up of rides with no description

    if extra != "": # line breaks are separate to avoid adding 2 extra blank lines to the message
        extra = f"\n\n{extra}"

    ride_message = f"{ride.name}\nOrganizer: {ride.organizer}\n\nDate/Time: {ride.nice_date()} @ {ride.time}\nPace: {ride.pace}{extra}"
    
    route_message = f"{route}" # force casting

    if route_message == "":
        message = ride_message
    else:
        message = ride_message + "\n\n" + route_message

    return message