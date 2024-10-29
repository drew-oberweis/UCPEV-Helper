import logging

from telegram import (
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
)

logger = logging.getLogger(__name__)

"""
This file contains simple commands that provide a canned response, with no secondary effects and no database interaction.
No database interaction until I stop being lazy and implement it.
"""

responses = {
    "welcome": "Welcome to UIUC PEV! Do /rules to check the rules of the group, and /help to see other commands!",
    "rules_header": "The rules of this group are generally pretty simple. They are:",
    "rules": """1. Wear a helmet\n
                2. WEAR A HELMET\n
                3. Follow the rules of the road\n
                4. Keep a safe riding distance\n
                5. Stagger while riding\n
                6. Don't wear loose clothes that might get caught\n
                7. Be careful where you point your flashlight\n
                8. Know your limits, and ride within them\n
                9. Communicate with your fellow riders\n
                10. Have fun!
            """,

    "nosedive": 'ayy lmao\nhttps://www.youtube.com/watch?v=kc6IEVV9mp0' # stolen directly from ChiPEV
}


async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    logger.info(f"Sending message: {message}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    return

async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Links command called")
    await send_message(update, context, "Nice try I havent fukin implemented this yet")

async def nosedive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Nosedive command called")
    await send_message(update, context, responses["nosedive"])
    return