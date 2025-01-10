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
import ride
from utils import send_message
import YoursTruly

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

async def inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Inline command called")
    await send_message(update, context, responses["inline"])
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

    # sort rides
    rides.sort()

    # include ride ID in message if user is an admin
    include_id = utils.is_admin(update.effective_user)
    # but don't if the user is the bot
    if update.effective_user.id == context.bot.id:
        include_id = False

    rides_msg = ""
    if (include_id):
        for ride in rides:
            rides_msg += f"{ride}\n{ride.id}\n{divider}\n"
    else:
        for ride in rides:
            rides_msg += f"{ride}\n{divider}\n"

    # cut off bottom line
    rides_msg = rides_msg[:-len(divider)-1]

    await send_message(update, context, f"Upcoming rides:\n\n{rides_msg}")

async def uploads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # sends the a message containing info on their uploaded rides
    logger.debug("Uploads command called")

    db_creds = db.DB_Credentials(
        host=os.getenv("postgres_host", None),
        user=os.getenv("postgres_user", None),
        password=os.getenv("postgres_pass", None),
        database=os.getenv("postgres_db", None)
    )

    session = db.Session(db_creds)

    user_id = update.effective_user.id
    user_uploads = session.get_ride_uploads(user_id=user_id)

    if not user_uploads:
        await send_message(update, context, "You have not uploaded any rides.")
        return
    
    divider = "----------------"

    uploads_msg = ""
    for ride in user_uploads:
        id = ride[0]

        ride = YoursTruly.Ride(f"./rides/{id}.json")

        ride_name = ride.getName()
        ride_author = ride.getRider()
        ride_id = ride.getId()

        uploads_msg += f"Name: {ride_name}\n{ride_author}\nRide ID: {ride_id}\n{divider}\n"

    # cut off bottom line
    uploads_msg = uploads_msg[:-len(divider)-1]

    await send_message(update, context, f"Your uploaded rides:\n\n{uploads_msg}")

    return

async def delete_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # delete a ride from the database and it's associated file

    db_creds = db.DB_Credentials(
        host=os.getenv("postgres_host", None),
        user=os.getenv("postgres_user", None),
        password=os.getenv("postgres_pass", None),
        database=os.getenv("postgres_db", None)
    )

    session = db.Session(db_creds)

    # pull ride id from message
    id = update.message.text.split(" ")[1]

    try:
        session.rm_ride_upload(id)
        os.remove(f"./rides/{id}.json")
    except Exception as e:
        await send_message(update, context, f"Ride not found.\n\nError {e}")
        return