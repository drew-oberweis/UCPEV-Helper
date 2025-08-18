import logging
from typing import Optional
import data
from utils import blind_send_message
import environment_handler

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

logger = logging.getLogger(__name__)

telegram_main_id = environment_handler.get_telegram_chat_id()

class Message:

    def __init__(self):
        self.user = None
        self.chat = None
        self.message = None
        self.discord_chat_id = None
        self.telegram_chat_id = None

    def set_user(self, user: str) -> None:
        self.user = user
    def set_chat(self, chat: str) -> None:
        self.chat = chat
    def set_message(self, message: str) -> None:
        self.message = message

    def __get_id_map(self) -> dict:
        log_level = environment_handler.get_log_level()
        if log_level == logging.DEBUG:
            logger.debug("Using dev channel map")
            id_map = data.chat_id_map_dev
        else:
            logger.debug("Using prod channel map")
            id_map = data.chat_id_map

        return id_map

    def set_telegram_topic_id(self, chat_id: int) -> None:

        id_map = self.__get_id_map()

        self.discord_chat_id = id_map.get(str(chat_id), None)
        self.telegram_chat_id = chat_id
        logger.debug(f"Set Discord chat ID: {self.discord_chat_id}")
        logger.debug(f"Set Telegram chat ID: {self.telegram_chat_id}")

    def set_discord_topic_id(self, chat_id: int) -> None:
        
        id_map = self.__get_id_map()

        self.discord_chat_id = chat_id
        self.telegram_chat_id = None

        for key, value in id_map.items():
            if value == chat_id:
                self.telegram_chat_id = key
                break

        logger.debug(f"Set Discord chat ID: {self.discord_chat_id}")
        logger.debug(f"Set Telegram chat ID: {self.telegram_chat_id}")
        
    def get_user(self) -> Optional[str]:
        return self.user
    def get_chat(self) -> Optional[str]:
        return self.chat
    def get_message(self) -> Optional[str]:
        return self.message
    def get_telegram_topic_id(self) -> Optional[int]:
        return self.telegram_chat_id
    def get_discord_topic_id(self) -> Optional[int]:
        return self.discord_chat_id
    def get_discord_webhook(self):
        return environment_handler.get_discord_webhook(self.discord_chat_id)

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
            messages_to_forward.append(message)

        self.queue = [msg for msg in self.queue if msg not in messages_to_forward]

        if messages_to_forward == []:
            return None

        return messages_to_forward

    def clear_queue(self) -> None:
        self.queue.clear()