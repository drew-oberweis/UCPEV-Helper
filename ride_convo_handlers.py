from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
import logging
import utils
import db
import os
import datetime

from ride import Ride

logger = logging.getLogger(__name__)

global db_creds

db_creds = db.DB_Credentials(
            host=os.getenv("postgres_host", None),
            user=os.getenv("postgres_user", None),
            password=os.getenv("postgres_pass", None),
            database=os.getenv("postgres_db", None)
        )

class ModifyRideMemory:
    def __init__(self):
        self.ride = None
        self.action = None
        self.field = None
        self.new_value = None

    def set_ride(self, ride):
        self.ride = ride
    def set_action(self, action):
        self.action = action
    def set_field(self, field):
        self.field = field
    def set_new_value(self, new_value):
        self.new_value = new_value

    def get_ride(self):
        return self.ride
    def get_action(self):
        return self.action
    def get_field(self):
        return self.field
    def get_new_value(self):
        return self.new_value

ride_type_regex = "^("
for i in Ride.ride_type_options:
    ride_type_regex += i + "|"
ride_type_regex = ride_type_regex[:-1] + ")$"

regex_all = "^(?!/cancel).*$" # match anything except /cancel
regex_date = "^(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/([0-9]{4})$"

global this_ride
global this_mod

class Ride_Helper_Functions:

    TYPE, DATE, TIME, MEETUP, DESTINATION, DESCRIPTION = range(6)

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

        return Ride_Helper_Functions.TYPE

    async def store_type_ask_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_ride
        this_ride.set_type(update.message.text)
        await update.message.reply_text(f"Ride type set to {this_ride.type}. Enter the date of the ride (MUST BE IN MM/DD/YYYY FORMAT, including zeroes for single digits)")
        return Ride_Helper_Functions.DATE

    async def store_date_ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_ride
        unix_date = int(datetime.datetime.strptime(update.message.text, "%m/%d/%Y").timestamp())
        this_ride.set_date(unix_date)
        await update.message.reply_text(f"Ride date set to {this_ride.nice_date()}. Enter the time of the ride" )
        return Ride_Helper_Functions.TIME

    async def store_time_ask_meetup(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_ride
        this_ride.set_time(update.message.text)
        await update.message.reply_text(f"Ride time set to {this_ride.time}. Enter the meetup location")
        return Ride_Helper_Functions.MEETUP

    async def store_meetup_ask_destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_ride
        this_ride.set_meetup(update.message.text)
        if(this_ride.type == "I2S" or this_ride.type == "Other"):
            await update.message.reply_text(f"Meetup location set to {this_ride.meetup_location}. Enter a description of the ride")
            return Ride_Helper_Functions.DESCRIPTION
        await update.message.reply_text(f"Meetup location set to {this_ride.meetup_location}. Enter the destination")
        return Ride_Helper_Functions.DESTINATION

    async def store_destination_ask_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_ride
        this_ride.set_destination(update.message.text)
        await update.message.reply_text(f"Destination set to {this_ride.destination}. Enter a description of the ride")
        return Ride_Helper_Functions.DESCRIPTION

    async def store_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_ride
        global db_creds
        this_ride.set_description(update.message.text)
        await update.message.reply_text(f"Description set to {this_ride.description}.")
        await update.message.reply_text("Ride creation complete. Complete ride info:\n\n{this_ride}")

        global db_creds

        session = db.Session(db_creds)


        session.add_ride(update.effective_user.id, this_ride.type, this_ride.date, this_ride.time, this_ride.meetup_location, this_ride.destination, this_ride.description)

        this_ride = None

        return ConversationHandler.END

    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Ride creation cancelled.")
        return ConversationHandler.END

ride_add_conv_handler = ConversationHandler(
        name="add_ride_handler",
        entry_points=[CommandHandler("add_ride", Ride_Helper_Functions.add_ride)],
        states= {
            Ride_Helper_Functions.TYPE: [MessageHandler(filters.Regex(ride_type_regex), Ride_Helper_Functions.store_type_ask_date)],
            Ride_Helper_Functions.DATE: [MessageHandler(filters.Regex(regex_date), Ride_Helper_Functions.store_date_ask_time)],
            Ride_Helper_Functions.TIME: [MessageHandler(filters.Regex(regex_all), Ride_Helper_Functions.store_time_ask_meetup)],
            Ride_Helper_Functions.MEETUP: [MessageHandler(filters.Regex(regex_all), Ride_Helper_Functions.store_meetup_ask_destination)],
            Ride_Helper_Functions.DESTINATION: [MessageHandler(filters.Regex(regex_all), Ride_Helper_Functions.store_destination_ask_description)],
            Ride_Helper_Functions.DESCRIPTION: [MessageHandler(filters.Regex(regex_all), Ride_Helper_Functions.store_description)]
        },
        fallbacks=[CommandHandler("cancel", Ride_Helper_Functions.cancel)]
    )

class Ride_Modify_Functions:

    SELECT, ACTION, READACTION, MODIFY, MODOPTIONS, DELETE = range(6)
    """
    SELECT = pick a ride to modify
    ACTION = pick what to do with the ride
    MODIFY = modify the ride
    DELETE = delete the ride

    Allowed modification fields:
    - type
    - date
    - time
    - meetup location
    - destination
    - description

    Flow:
    1. Select a ride
    2. Select an action (Modify, Delete)
    3. If Delete, confirm deletion
    4. If Modify, select a field to modify
    5. Modify the field
    """

    mod_options_keyboard = [
        ["Type", "Date"],
        ["Time", "Meetup location"],
        ["Destination", "Description"]
    ]

    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Ride modification cancelled.")
        return ConversationHandler.END
    
    async def select_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.log(logging.DEBUG, "Modify ride command called")

        # check if the user is in a group chat
        if update.effective_chat.type == "group" or update.effective_chat.type == "supergroup":
            await update.message.reply_text("This command can only be used in a private chat.")
            return ConversationHandler.END

        # make sure the user is an admin
        is_admin = await utils.is_admin(update.effective_user)
        if not is_admin:
            logger.info(f"Unauthorized access to command modify_ride by user {update.effective_user.id}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You are not authorized to use this command.")
            return ConversationHandler.END

        current_timestamp = datetime.datetime.now().timestamp()

        session = db.Session(db_creds)
        rides = session.get_rides(limit=5, ride_time_after=current_timestamp)

        ride_names = []

        for i in rides:
            ride_names.append(i.str_one_line())

        keyboard_buttons = [ride_names]

        logger.log(logging.DEBUG, "Available keyboard options: %s", keyboard_buttons)

        await update.message.reply_text("Select a ride to modify", 
                                        reply_markup=ReplyKeyboardMarkup(keyboard_buttons, 
                                                                         one_time_keyboard=True, 
                                                                         input_field_placeholder="Select a ride"))
        return Ride_Modify_Functions.ACTION
    
    async def select_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_mod

        if update.message.text == "/cancel":
            await update.message.reply_text("Ride modification cancelled.")
            return ConversationHandler.END
        
        this_mod = ModifyRideMemory()

        session = db.Session(db_creds)

        this_mod.set_ride(session.get_ride_by_str(ride_str=update.message.text))

        if this_mod.get_ride() == None:
            await update.message.reply_text("Invalid ride. Please select a ride from the list.")
            return Ride_Modify_Functions.SELECT
        
        await update.message.reply_text(f"Selected ride:\n{this_mod.get_ride()}\n\nSelect an action to perform on this ride", 
                                        reply_markup=ReplyKeyboardMarkup([["Modify", "Delete"]],
                                                                         one_time_keyboard=True, 
                                                                         input_field_placeholder="Select an action"))
        return Ride_Modify_Functions.READACTION
    
    async def read_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text == "/cancel":
            await update.message.reply_text("Ride modification cancelled.")
            return ConversationHandler.END

        if update.message.text == "Modify":
            await update.message.reply_text("Select parameter to modify",
                                            reply_markup=ReplyKeyboardMarkup(Ride_Modify_Functions.mod_options_keyboard,
                                                                             one_time_keyboard=True,
                                                                            input_field_placeholder="Select a parameter to modify"))
            return Ride_Modify_Functions.MODOPTIONS
        elif update.message.text == "Delete":
            yesno_keyboard = [["Yes", "No"]]
            await update.message.reply_text("Are you sure you want to delete this ride? (yes/no)",
                                            reply_markup=ReplyKeyboardMarkup(yesno_keyboard,
                                                                             one_time_keyboard=True,
                                                                             input_field_placeholder="yes/no"))
            return Ride_Modify_Functions.DELETE
        else:
            await update.message.reply_text("Invalid action. Please select an action from the list.")
            return Ride_Modify_Functions.ACTION
        
    async def mod_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text == "/cancel":
            await update.message.reply_text("Ride modification cancelled.")
            return ConversationHandler.END

        if update.message.text not in ["Type", "Date", "Time", "Meetup location", "Destination", "Description"]:
            await update.message.reply_text("Invalid option. Please select a valid option from the list.")
            return Ride_Modify_Functions.MODOPTIONS
        
        global this_mod
        this_mod.set_field(update.message.text)

        await update.message.reply_text(f"Enter new value for {update.message.text}")
        return Ride_Modify_Functions.MODIFY
    
    async def modify_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text == "/cancel":
            await update.message.reply_text("Ride modification cancelled.")
            return ConversationHandler.END

        global this_mod
        this_mod.set_new_value(update.message.text)

        session = db.Session(db_creds)

        if this_mod.get_field() == "Type":
            session.update_ride(this_mod.get_ride().id, "type", this_mod.get_new_value())
        elif this_mod.get_field() == "Date":
            unix_date = datetime.datetime.strptime(this_mod.get_new_value(), "%m/%d/%Y").timestamp()
            session.update_ride(this_mod.get_ride().id, "ride_date", unix_date)
        elif this_mod.get_field() == "Time":
            session.update_ride(this_mod.get_ride().id, "time", this_mod.get_new_value())
        elif this_mod.get_field() == "Meetup location":
            session.update_ride(this_mod.get_ride().id, "meetup_location", this_mod.get_new_value())
        elif this_mod.get_field() == "Destination":
            session.update_ride(this_mod.get_ride().id, "destination", this_mod.get_new_value())
        elif this_mod.get_field() == "Description":
            session.update_ride(this_mod.get_ride().id, "description", this_mod.get_new_value())

        await update.message.reply_text(f"Modifying {this_mod.get_field()} to {this_mod.get_new_value()}")

        return ConversationHandler.END

    async def delete_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text == "/cancel":
            await update.message.reply_text("Ride modification cancelled.")
            return ConversationHandler.END

        if update.message.text == "Yes":
            global this_mod
            session = db.Session(db_creds)
            session.rm_ride(this_mod.get_ride().id)
            await update.message.reply_text("Ride deleted.")
        else:
            await update.message.reply_text("Ride deletion cancelled.")

        return ConversationHandler.END

modify_ride_conv_handler = ConversationHandler(
        name="modify_ride_handler",
        entry_points=[CommandHandler("modify_ride", Ride_Modify_Functions.select_ride)],
        states = {
            Ride_Modify_Functions.ACTION: [MessageHandler(filters.Regex(regex_all), Ride_Modify_Functions.select_action)],
            Ride_Modify_Functions.READACTION: [MessageHandler(filters.Regex(regex_all), Ride_Modify_Functions.read_action)],
            Ride_Modify_Functions.MODIFY: [MessageHandler(filters.Regex(regex_all), Ride_Modify_Functions.modify_ride)],
            Ride_Modify_Functions.MODOPTIONS: [MessageHandler(filters.Regex(regex_all), Ride_Modify_Functions.mod_options)],
            Ride_Modify_Functions.DELETE: [MessageHandler(filters.Regex(regex_all), Ride_Modify_Functions.delete_ride)]
        },
        fallbacks=[CommandHandler("cancel", Ride_Modify_Functions.cancel)]
)