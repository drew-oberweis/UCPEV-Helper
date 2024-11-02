import logging
from typing import Optional

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

import db
from discord_webhook import DiscordWebhook

logger = logging.getLogger(__name__)

async def is_admin(chat: Chat, user: User, context: ContextTypes.DEFAULT_TYPE):
    admins_raw = await context.bot.get_chat_administrators(chat.id)

    admins = []
    for i in range(len(admins_raw)):
        admins.append(admins_raw[i].user.id)

    status = user.id in admins
    logger.log(logging.INFO, f"User {user.id} is{' not' if not status else ''} an admin in chat {chat.id}")
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