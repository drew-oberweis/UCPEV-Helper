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
from utils import UpdateBundle
import sheets_interface as shit

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
    ub = UpdateBundle(update, context)
    logger.debug("Links command called")
    await ub.send_message(responses["links"])

async def nosedive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ub = UpdateBundle(update, context)
    logger.debug("Nosedive command called")
    await ub.send_message(responses["nosedive"])
    return

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ub = UpdateBundle(update, context)
    logger.debug("Rules command called")

    rules_msg = responses["rules_header"] + "\n\n"
    for i in responses["rules"]:
        rules_msg += f"- {i}\n"
    await ub.send_message(rules_msg)

    return

async def helmet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ub = UpdateBundle(update, context)
    logger.debug("Helmet command called")
    await ub.send_message(responses["helmet"])
    return

async def pads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ub = UpdateBundle(update, context)
    logger.debug("Pads command called")
    await ub.send_message(responses["pads"])
    return

async def codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ub = UpdateBundle(update, context)
    logger.debug("Codes command called")
    await ub.send_message(responses["codes"])
    return

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):

    ub = UpdateBundle(update, context)

    was_member, is_member = utils.extract_status_change(update.chat_member)

    if not was_member and is_member:
        logger.debug("Welcome command called")
        await ub.send_message(responses["welcome"])
    return

async def i2s(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ub = UpdateBundle(update, context)
    logger.debug("I2S command called")
    await ub.send_message(responses["i2s"])
    return

async def inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ub = UpdateBundle(update, context)
    logger.debug("Inline command called")
    await ub.send_message(responses["inline"])
    return

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ub = UpdateBundle(update, context)
    logger.debug("Help command called")
    help_msg = "Here are the commands you can use:\n"
    for i in commands: # TODO: Make this filter by what the user can actually do
        help_msg += f"/{i} - {command_descriptions[i]}\n"

    is_admin = await utils.is_admin(update.effective_user)

    if is_admin:
        help_msg += "\n\nAdmin commands:\n"
        for i in admin_commands:
            help_msg += f"/{i} - {admin_command_descriptions[i]}\n"

    await ub.send_message(help_msg)
    return

async def econtact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ub = UpdateBundle(update, context)
    logger.debug("Emergency contact command called")
    await ub.send_message(f"Please fill out our emergency contact form: {data.emergency_contact_form_url}")
    return

async def rides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ub = UpdateBundle(update, context)

    ride_inf = shit.get_rides()[0]

    organizer = ride_inf[0]
    name = ride_inf[1]
    date = ride_inf[2]
    time = ride_inf[3]
    route = ride_inf[4]
    pace = ride_inf[5]
    extra = ride_inf[6]

    route_inf = shit.get_route(route)

    start_loc = route_inf[1]
    start_pin = route_inf[2]
    notable_loc = route_inf[3]
    end_loc = route_inf[4]
    end_pin = route_inf[5]
    dist = route_inf[6]
    gaia_link = route_inf[7]
    route_desc = route_inf[8]
    route_extra = route_inf[9]

    if extra != "":
        extra = f"\n\n{extra}"

    ride_message = f"{name}\nOrganizer: {organizer}\n\nDate/Time: {date} @ {time}\nPace: {pace}{extra}"
    
    if start_pin == "":
        start_msg = f"Start Location: {start_loc}"
    else:
        start_msg = f"Start Location: {start_loc} ({start_pin})"

    if end_pin == "":
        end_msg = f"End Location: {end_loc}"
    else:
        end_msg = f"End Location: {end_loc} ({end_pin})"

    route_message = f"Route Name: {route}\n{start_msg}\n{end_msg}\nPOI: {notable_loc}\nDistance: {dist} miles\nGAIA Link: {gaia_link}\n\nRoute Description: {route_desc}\n\n{route_extra}"

    message = ride_message + "\n\n" + route_message

    await ub.send_message(message)