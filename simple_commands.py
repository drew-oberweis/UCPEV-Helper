import logging
import utils

from telegram import (
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
)
from telegram.constants import ParseMode
import data

responses = data.responses
commands_descriptions = data.commands_descriptions

commands = ["nosedive", "rules", "links", "codes", "helmet", "help", "pads"]

logger = logging.getLogger(__name__)

"""
This file contains simple commands that provide a canned response, with no secondary effects and no database interaction.
No database interaction until I stop being lazy and implement it.
Eventually all of these responses should pull dynamically from the database to allow updates without code changes.
"""


async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    logger.debug(f"Sending message: {message}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.MARKDOWN_V2)
    return

async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Links command called")
    await send_message(update, context, responses["links"])

async def nosedive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Nosedive command called")
    await send_message(update, context, responses["nosedive"])
    return

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Rules command called")

    rules_msg = responses["rules_header"] + "\n\n" + responses["rules"]
    await send_message(update, context, rules_msg)

    return

async def helmet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Helmet command called")
    await send_message(update, context, responses["helmet"])
    return

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Help command called")
    help_msg = "Here are the commands you can use:\n"
    for i in commands: # TODO: Make this filter by what the user can actually do
        help_msg += f"/{i} \- {commands_descriptions[i]}\n"
    await send_message(update, context, help_msg)
    return

async def pads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Pads command called")
    await send_message(update, context, responses["pads"])
    return

async def codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Codes command called")
    await send_message(update, context, responses["codes"])
    return

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):

    was_member, is_member = utils.extract_status_change(update.chat_member)

    if not was_member and is_member:
        logger.debug("Welcome command called")
        await send_message(update, context, responses["welcome"])
    return

async def i2s(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("I2S command called")
    await send_message(update, context, responses["i2s"])
    return