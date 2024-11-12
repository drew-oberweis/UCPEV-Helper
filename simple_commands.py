import logging
import utils
import os
import datetime

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
import db

responses = data.responses
command_descriptions = data.command_descriptions
admin_command_descriptions = data.admin_command_descriptions
commands = data.commands
admin_commands = data.admin_commands

logger = logging.getLogger(__name__)

"""
This file contains simple commands that provide a canned response, with no secondary effects and no database interaction.
No database interaction until I stop being lazy and implement it.
Eventually all of these responses should pull dynamically from the database to allow updates without code changes.
"""


async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    logger.debug(f"Sending message: {message}")
    # reply to the message that called this command
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)
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

    rules_msg = responses["rules_header"] + "\n\n"
    for i in responses["rules"]:
        rules_msg += f"- {i}\n"
    await send_message(update, context, rules_msg)

    return

async def helmet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Helmet command called")
    await send_message(update, context, responses["helmet"])
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

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Help command called")
    help_msg = "Here are the commands you can use:\n"
    for i in commands: # TODO: Make this filter by what the user can actually do
        help_msg += f"/{i} - {command_descriptions[i]}\n"

    is_admin = await utils.is_admin(update.effective_user)

    if is_admin:
        help_msg += "\n\nAdmin commands:\n"
        for i in admin_commands:
            help_msg += f"/{i} - {admin_command_descriptions[i]}\n"

    await send_message(update, context, help_msg)
    return

async def rides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Rides command called")
    
    db_creds = db.DB_Credentials(
        host=os.getenv("postgres_host", None),
        user=os.getenv("postgres_user", None),
        password=os.getenv("postgres_pass", None),
        database=os.getenv("postgres_db", None)
    )

    session = db.Session(db_creds)
    curtime = datetime.datetime.now().timestamp()
    yesterday = curtime - 86400
    

    rides = session.get_rides(ride_time_after=yesterday)

    # if rides is empty, return a message saying so
    if not rides:
        await send_message(update, context, "There are no upcoming rides.")
        return

    divider = "----------------"

    rides_msg = ""
    for ride in rides:
        rides_msg += f"{ride}\n{divider}\n"

    # cut off bottom line
    rides_msg = rides_msg[:-len(divider)-1]

    await send_message(update, context, f"Upcoming rides:\n\n{rides_msg}")