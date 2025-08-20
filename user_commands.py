import logging
import utils

from telegram import (
    Update,
)
from telegram.ext import (
    ContextTypes,
)
import data
from utils import UpdateBundle
import sheets_interface as shit

import task_schedulers

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

    is_admin = await utils.is_admin(update, context)

    if is_admin:
        help_msg += "\n\nAdmin commands:\n"
        for i in admin_commands:
            help_msg += f"/{i} - {admin_command_descriptions[i]}\n"

    await ub.send_message(help_msg)
    return

async def econtact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ub = UpdateBundle(update, context)
    logger.debug("Emergency contact command called")
    await ub.send_message(f"Please fill out this form to provide group admins with emergency contact information: {data.emergency_contact_form_url}")
    return

async def rides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ub = UpdateBundle(update, context)

    # get number from message
    try:
        number = int(context.args[0])
    except ValueError:
       await ub.send_message("Please provide a valid number of rides.")
       return
    except IndexError:
        number = None

    if number is None:
        try:
            # get the next ride
            rides = shit.get_upcoming_rides()
            ride = rides[0]
        except IndexError as e:
            await ub.send_message("There are no scheduled rides.")
            return

        message = utils.generate_ride_text(ride)
    else:

        # if command is run in non-dm, delete message
        if not update.message.chat.type == "private":
            response = await ub.send_message("This command can only be used in private messages. Please use the command in a private chat with @uc_pev_bot.")

            # schedule deletion of message in 10 seconds
            response_data = {
                "chat_id": update.effective_chat.id,
                "message_id": response.id
            }
            task_schedulers.add_single_task(utils.scheduled_delete_message, 10, response_data)

            message_data = {
                "chat_id": update.effective_chat.id,
                "message_id": update.effective_message.id
            }
            task_schedulers.add_single_task(utils.scheduled_delete_message, 10, message_data)
            return

        message = ""
        separator = "\n\n--------------------------------\n\n"
        try:
            rides = shit.get_upcoming_rides()
            for i in range(min(number, len(rides))):
                message += utils.generate_ride_text(rides[i]) + separator
            
            # remove the final separator
            message = message.rstrip(separator)
        except Exception as e:
            await ub.send_message(f"There was an error retrieving the rides: {e}")
            return

    await ub.send_message(message)