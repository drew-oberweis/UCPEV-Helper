from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
import logging
import utils
import db
import os
import datetime

logger = logging.getLogger(__name__)


TYPE, DATE, TIME, MEETUP, DESTINATION, DESCRIPTION = range(6)

class Ride:
    def __init__(self):
        self.type = ""
        self.date = ""
        self.time = ""
        self.meetup_location = ""
        self.destination = ""
        self.description = ""

    def __str__(self):
        # convert unix timestamp into mm/dd/yyyy format
        if (self.type == "Short" or self.type == "Long"):
            return f"Ride type: {self.type}\nDate: {self.nice_date()}\nTime: {self.time}\nMeetup: {self.meetup_location}\nDestination: {self.destination}\nDescription: {self.description}"
        else:
            return f"Ride type: {self.type}\nDate: {self.date}\nTime: {self.time}\nMeetup: {self.meetup_location}\nDescription: {self.description}" # skip destination for I2S and Other rides
        
    def nice_date(self):
        return datetime.datetime.fromtimestamp(self.date).strftime("%m/%d/%Y")

    def set_type(self, ride_type):
        self.type = ride_type
    def set_date(self, ride_date):
        self.date = int(float(ride_date))
    def set_time(self, ride_time):
        self.time = ride_time
    def set_meetup(self, meetup_location):
        self.meetup_location = meetup_location
    def set_destination(self, destination):
        self.destination = destination
    def set_description(self, description):
        self.description = description

    ride_type_options = ["Short", "Long", "I2S", "Other"]



ride_type_regex = "^("
for i in Ride.ride_type_options:
    ride_type_regex += i + "|"
ride_type_regex = ride_type_regex[:-1] + ")$"

regex_all = "^(?!/cancel).*$" # match anything except /cancel
regex_date = "^(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/([0-9]{4})$"

global this_ride

async def add_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.log(logging.DEBUG, "Add ride command called")

    global this_ride
    this_ride = Ride()

    # check if the user is in a group chat
    if update.effective_chat.type == "group" or update.effective_chat.type == "supergroup":
        await update.message.reply_text("This command can only be used in a private chat.")
        return ConversationHandler.END

    # make sure the user is an admin
    is_admin = await utils.is_admin(update.effective_user)
    if not is_admin:
        logger.info(f"Unauthorized access to command add_ride by user {update.effective_user.id}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You are not authorized to use this command.")
        return ConversationHandler.END

    reply_keyboard = [[i for i in Ride.ride_type_options]]

    logger.log(logging.DEBUG, "Available keyboard options: %s", reply_keyboard)

    await update.message.reply_text("Beginning ride creation process. Follow all prompts to add a ride, or type /cancel to exit.\n\nSelect ride type", 
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, 
                                                                    one_time_keyboard=True, 
                                                                    input_field_placeholder="Select a ride type"))

    return TYPE

async def store_type_ask_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global this_ride
    this_ride.set_type(update.message.text)
    await update.message.reply_text(f"Ride type set to {this_ride.type}. Enter the date of the ride")
    return DATE

async def store_date_ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global this_ride
    unix_date = datetime.datetime.strptime(update.message.text, "%m/%d/%Y").timestamp()
    this_ride.set_date(unix_date)
    await update.message.reply_text(f"Ride date set to {this_ride.nice_date()}. Enter the time of the ride" )
    return TIME

async def store_time_ask_meetup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global this_ride
    this_ride.set_time(update.message.text)
    await update.message.reply_text(f"Ride time set to {this_ride.time}. Enter the meetup location")
    return MEETUP

async def store_meetup_ask_destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global this_ride
    this_ride.set_meetup(update.message.text)
    if(this_ride.type == "I2S" or this_ride.type == "Other"):
        await update.message.reply_text(f"Meetup location set to {this_ride.meetup_location}. Enter a description of the ride")
        return DESCRIPTION
    await update.message.reply_text(f"Meetup location set to {this_ride.meetup_location}. Enter the destination")
    return DESTINATION

async def store_destination_ask_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global this_ride
    this_ride.set_destination(update.message.text)
    await update.message.reply_text(f"Destination set to {this_ride.destination}. Enter a description of the ride")
    return DESCRIPTION

async def store_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global this_ride
    this_ride.set_description(update.message.text)
    await update.message.reply_text(f"Description set to {this_ride.description}. Ride creation complete. Complete ride info:\n\n{this_ride}")

    # send the ride to the database
    
    db_creds = db.DB_Credentials(
        host=os.getenv("postgres_host", None),
        user=os.getenv("postgres_user", None),
        password=os.getenv("postgres_pass", None),
        database=os.getenv("postgres_db", None)
    )

    session = db.Session(db_creds)


    session.add_ride(update.effective_user.id, this_ride.type, this_ride.date, this_ride.time, this_ride.meetup_location, this_ride.destination, this_ride.description)

    this_ride = None

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ride creation cancelled.")
    return ConversationHandler.END

ride_add_conv_handler = ConversationHandler(
        name="add_ride_handler",
        entry_points=[CommandHandler("add_ride", add_ride)],
        states= {
            TYPE: [MessageHandler(filters.Regex(ride_type_regex), store_type_ask_date)],
            DATE: [MessageHandler(filters.Regex(regex_date), store_date_ask_time)],
            TIME: [MessageHandler(filters.Regex(regex_all), store_time_ask_meetup)],
            MEETUP: [MessageHandler(filters.Regex(regex_all), store_meetup_ask_destination)],
            DESTINATION: [MessageHandler(filters.Regex(regex_all), store_destination_ask_description)],
            DESCRIPTION: [MessageHandler(filters.Regex(regex_all), store_description)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )