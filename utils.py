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

from discord_webhook import DiscordWebhook
import data
import environment_handler

token = environment_handler.get_telegram_token()

logger = logging.getLogger(__name__)

#TODO: Make this a config file and not hardcoded
chat_id_map = {
    "discord": {
        "general": 1186544426835791874,
        "Topic": 1186544831892312164
    },
    "telegram": {
        "general": "",  # Telegram's "General" chat doesn't have a channel ID, it is just the group chat ID
        "replicate": 3 
    }
}

telegram_main_id = -1002409253277

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

class Message:

    def __init__(self):
        self.dest_platform = None
        self.user = None
        self.chat = None
        self.message = None
        self.discord_chat_id = None
        self.telegram_chat_id = None



    def set_dest_platform(self, platform: str) -> None:
        if platform in ["telegram", "discord"]:
            self.dest_platform = platform
        else:
            raise ValueError("Invalid platform. Must be 'telegram' or 'discord'.")

    def set_user(self, user: str) -> None:
        self.user = user
    def set_chat(self, chat: str) -> None:
        self.chat = chat
    def set_message(self, message: str) -> None:
        self.message = message

    def set_chat_id(self, dest_platform: str, chat_id: int) -> None:
        if dest_platform not in ["telegram", "discord"]:
            raise ValueError("Invalid platform. Must be 'telegram' or 'discord'.")

        # convert the chat ID to the opposite platform's chat ID
        if dest_platform == "discord":
            self.telegram_chat_id = chat_id
            self.discord_chat_id = chat_id_map["discord"].get(self.chat, None)
            logger.debug(f"Set Discord chat ID: {self.discord_chat_id} for chat {self.chat}")
            logger.debug(f"Set Telegram chat ID: {self.telegram_chat_id} for chat {self.chat}")
        elif dest_platform == "telegram":
            self.discord_chat_id = chat_id
            self.telegram_chat_id = chat_id_map["telegram"].get(self.chat, None)
            logger.debug(f"Set Telegram chat ID: {self.telegram_chat_id} for chat {self.chat}")
            logger.debug(f"Set Discord chat ID: {self.discord_chat_id} for chat {self.chat}")
        

    def get_dest_platform(self) -> Optional[str]:
        return self.dest_platform
    def get_user(self) -> Optional[str]:
        return self.user
    def get_chat(self) -> Optional[str]:
        return self.chat
    def get_message(self) -> Optional[str]:
        return self.message

    def get_chat_id(self) -> Optional[int]:
        if self.dest_platform == "telegram":
            return self.telegram_chat_id
        elif self.dest_platform == "discord":
            return self.discord_chat_id
        return None

class MessageQueue:
    def __init__(self):
        self.queue = []

    def add_message(self, message: Message) -> None:
        self.queue.append(message)

    def get_queue(self, platform: str) -> list:
        if platform not in ["telegram", "discord"]:
            raise ValueError("Invalid platform. Must be 'telegram' or 'discord'.")

        messages_to_forward = []
        for message in self.queue:
            if message.get_dest_platform() == platform:
                messages_to_forward.append(message)

        self.queue = [msg for msg in self.queue if msg not in messages_to_forward]

        if messages_to_forward == []:
            return None

        return messages_to_forward

    def clear_queue(self) -> None:
        self.queue.clear()

async def check_queue(context: ContextTypes.DEFAULT_TYPE):
    """Check the queue for messages to forward."""

    q = context.job.data

    messages = q.get_queue("telegram")
    if messages:
        for message in messages:
            await blind_send_message(
                chat_id=telegram_main_id,
                message=message.get_message(),
                topic_id=message.get_chat_id(),
                context=context,
            )
            logger.debug(f"Forwarded message to Telegram: {message.get_message()} from {message.get_user()} in chat {message.get_chat()} with ID {message.get_chat_id()}")
    else:
        logger.debug("No messages to forward to Telegram in the queue.")

    def do_nothing():
        return None

    return do_nothing() # this is so stupid

async def blind_send_message(chat_id: int, message: str, topic_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message to a chat without any context."""
    try:
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML, message_thread_id=topic_id)
    except Exception as e:
        raise Exception(f"Failed to send message to chat {chat_id}: {e}")


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

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
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