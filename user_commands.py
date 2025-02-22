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

async def rides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Rides command called")
    ub = UpdateBundle(update, context)
    
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
        await ub.send_message("There are no upcoming rides.")
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

    await ub.send_message(f"Upcoming rides:\n\n{rides_msg}")

async def trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # sends the a message containing info on their uploaded rides

    ub = UpdateBundle(update, context)

    logger.debug("Trips command called")

    db_creds = db.DB_Credentials(
        host=os.getenv("postgres_host", None),
        user=os.getenv("postgres_user", None),
        password=os.getenv("postgres_pass", None),
        database=os.getenv("postgres_db", None)
    )

    session = db.Session(db_creds)

    user_id = ub.get_update().effective_user.id
    user_trips = session.get_trips(user_id=user_id)

    if not user_trips:
        await ub.send_message("You have not uploaded or tracked any trips.")
        return
    
    divider = "----------------"

    trips_msg = ""
    for trip in user_trips:
        id = trip[0]

        trip = YoursTruly.Trip(f"./trips/{id}.json")

        ride_name = trip.getName()
        ride_id = trip.getId()

        # pull ride author id from database
        trip_author_id = session.get_trip_author(id)
        trip_author = session.get_user(trip_author_id)[0]
        trip_author_message = f"Uploaded by <a href='tg://user?id={trip_author}'>{trip_author}</a>"

        logger.log(logging.DEBUG, f"Trip name: {ride_name}\nTrip author: {trip_author}Trip Author ID: {trip_author_id}\nTrip ID: {ride_id}")

        trips_msg += f"Name: {ride_name}\n{trip_author_message}\nTrip ID: {ride_id}\n{divider}\n"

    # cut off bottom line
    trips_msg = trips_msg[:-len(divider)-1]

    await ub.send_message(f"Your uploaded trips:\n\n{trips_msg}")

    return

async def delete_trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # delete a ride from the database and it's associated file
    ub = UpdateBundle(update, context)

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
        session.remove_trip(id)
        os.remove(f"./rides/{id}.json")
    except Exception as e:
        await ub.send_message(f"Trip not found.\n\nError {e}")
        return
    
    await ub.send_message(f"Trip {id} deleted.")

async def trip_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ub = UpdateBundle(update, context)

    db_creds = db.DB_Credentials(
        host=os.getenv("postgres_host", None),
        user=os.getenv("postgres_user", None),
        password=os.getenv("postgres_pass", None),
        database=os.getenv("postgres_db", None)
    )

    session = db.Session(db_creds)

    # pull ride id from message
    id = update.message.text.split(" ")[1]

    trip = YoursTruly.Trip(f"./trips/{id}.json")

    response = f"Stats for trip {trip.getName()}:\n\n"

    speedMult = 2.237 # m/s to mph
    distDiv = 1609.34 # m to miles
    elevationMult = 3.281 # m to feet

    #TODO: These values are fucked, fix them

    escTopSpeed = trip.getEscTopSpeed() * speedMult
    gpsTopSpeed = trip.getGpsTopSpeed() * speedMult
    escAverageSpeed = trip.getEscAverageSpeed() * speedMult
    gpsAverageSpeed = trip.getGpsAverageSpeed() * speedMult
    escDistance = trip.getEscTotalDistance() / distDiv
    gpsDistance = trip.getGpsTotalDistance() / distDiv
    elevationGain = trip.getElevationGain() * elevationMult
    elevationLoss = trip.getElevationLoss() * elevationMult
    startTime = trip.getStartTime()
    endTime = trip.getEndTime()
    duration = trip.getDuration()

    # round all values to 2 decimal places
    escTopSpeed = round(escTopSpeed, 2)
    gpsTopSpeed = round(gpsTopSpeed, 2)
    escAverageSpeed = round(escAverageSpeed, 2)
    gpsAverageSpeed = round(gpsAverageSpeed, 2)
    escDistance = round(escDistance, 2)
    gpsDistance = round(gpsDistance, 2)
    elevationGain = round(elevationGain, 2)
    elevationLoss = round(elevationLoss, 2)
    duration = round(duration, 2)

    response += "Stats are formatted [ESC : GPS]\n\n"

    response += f"Top Speed: {escTopSpeed} : {gpsTopSpeed} mph\n"
    response += f"Average Speed: {escAverageSpeed} : {gpsAverageSpeed} mph\n"
    response += f"Distance: {escDistance} : {gpsDistance} miles\n"
    response += f"Elevation Gain: {elevationGain} feet\n"
    response += f"Elevation Loss: {elevationLoss} feet\n"
    response += f"\n"
    response += f"Start Time: {startTime}\n"
    response += f"End Time: {endTime}\n"
    response += f"Duration: {duration} seconds\n"

    await ub.send_message(response)

    return