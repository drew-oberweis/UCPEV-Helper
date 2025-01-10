from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
import logging
import utils
import db
import os
import datetime

from ride import Ride, Verifiers

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

ride_type_keyboard = ReplyKeyboardMarkup([[i for i in Ride.ride_type_options]], one_time_keyboard=True, input_field_placeholder="Select a type")

ride_pace_regex = "^("
for i in Ride.ride_pace_options:
    ride_pace_regex += i + "|"
ride_pace_regex = ride_pace_regex[:-1] + ")$"

ride_pace_keyboard = ReplyKeyboardMarkup([[i for i in Ride.ride_pace_options]], one_time_keyboard=True, input_field_placeholder="Select a pace")

regex_all = ".*" # match everything
regex_date = "^(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/([0-9]{4})$"

global this_ride
global this_mod

class Ride_Helper_Functions:

    TYPE, DATE, TIME, MEETUP, DESTINATION, PACE, DESCRIPTION = range(7)

    async def add_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.log(logging.DEBUG, "Add ride command called")

        global this_ride
        this_ride = Ride()

        # check if the user is in a group chat
        if update.effective_chat.type == "group" or update.effective_chat.type == "supergroup":
            await update.message.reply_text("This command can only be used in a private chat.")
            logger.log(logging.INFO, f"User {update.effective_user.id} attempted to use command add_ride in a group chat")
            return ConversationHandler.END

        # make sure the user is an admin
        is_admin = await utils.is_admin(update.effective_user)
        if not is_admin:
            logger.info(f"Unauthorized access to command add_ride by user {update.effective_user.id}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You are not authorized to use this command.")
            return ConversationHandler.END

        logger.log(logging.DEBUG, f"User {update.effective_user.id} started ride creation process")

        await update.message.reply_text("Beginning ride creation process. Follow all prompts to add a ride, or type /cancel to exit.\n\nSelect ride type", 
                                        reply_markup=ride_type_keyboard)

        return Ride_Helper_Functions.TYPE

    async def store_type_ask_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_ride
        try:
            this_ride.set_type(update.message.text)
        except ValueError:
            await update.message.reply_text("Invalid ride type. Please select a valid ride type from the list.",
                                             reply_markup=ride_type_keyboard)
            return Ride_Helper_Functions.TYPE
        logger.log(logging.DEBUG, f"Ride type set to {this_ride.type} by {update.effective_user.id}")
        await update.message.reply_text(f"Ride type set to {this_ride.type}. Enter the date of the ride (MUST BE IN MM/DD/YYYY FORMAT, including zeroes for single digits)")
        return Ride_Helper_Functions.DATE

    async def store_date_ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_ride
        
        if(not(Verifiers.verify_date(update.message.text))):
            await update.message.reply_text("Invalid date. Please enter a valid date in MM/DD/YYYY format.")
            return Ride_Helper_Functions.DATE
        
        this_ride.set_date(update.message.text)

        logger.log(logging.DEBUG, f"Ride date set to {this_ride.date} by {update.effective_user.id}")
        await update.message.reply_text(f"Ride date set to {this_ride.nice_date()}. Enter the time of the ride" )
        return Ride_Helper_Functions.TIME

    async def store_time_ask_meetup(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_ride
        this_ride.set_time(update.message.text)
        logger.log(logging.DEBUG, f"Ride time set to {this_ride.time} by {update.effective_user.id}")
        await update.message.reply_text(f"Ride time set to {this_ride.time}. Enter the meetup location")
        return Ride_Helper_Functions.MEETUP

    async def store_meetup_ask_destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_ride
        this_ride.set_meetup(update.message.text)
        if(this_ride.type == "I2S" or this_ride.type == "Other"): # skip destination and pace for I2S and Other rides
            logger.log(logging.DEBUG, f"Ride meetup location set to {this_ride.meetup_location} by {update.effective_user.id}")
            await update.message.reply_text(f"Meetup location set to {this_ride.meetup_location}. Enter a description of the ride")
            return Ride_Helper_Functions.DESCRIPTION
        logger.log(logging.DEBUG, f"Ride meetup location set to {this_ride.meetup_location} by {update.effective_user.id}")
        await update.message.reply_text(f"Meetup location set to {this_ride.meetup_location}. Enter the destination of the ride")
        return Ride_Helper_Functions.DESTINATION
    
    async def store_destination_ask_pace(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_ride
        this_ride.set_destination(update.message.text)
        logger.log(logging.DEBUG, f"Ride destination set to {this_ride.destination} by {update.effective_user.id}")
        await update.message.reply_text(f"Destination set to {this_ride.destination}. Enter the pace of the ride",
                                        reply_markup=ride_pace_keyboard)
        return Ride_Helper_Functions.PACE

    async def store_pace_ask_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_ride
        try:
            this_ride.set_pace(update.message.text)
        except ValueError:
            await update.message.reply_text("Invalid pace. Please select a valid pace from the list.",
                                             reply_markup=ride_pace_keyboard)
            return Ride_Helper_Functions.PACE
        logger.log(logging.DEBUG, f"Ride pace set to {this_ride.pace} by {update.effective_user.id}")
        await update.message.reply_text(f"Pace set to {this_ride.pace}. Enter a description of the ride")
        return Ride_Helper_Functions.DESCRIPTION

    async def store_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_ride
        global db_creds
        this_ride.set_description(update.message.text)
        logger.log(logging.DEBUG, f"Ride description set to {this_ride.description} by {update.effective_user.id}")
        await update.message.reply_text(f"Description set to {this_ride.description}.")
        await update.message.reply_text(f"Ride creation complete. Complete ride info:\n\n{this_ride}")

        global db_creds

        session = db.Session(db_creds)

        session.add_ride(update.effective_user.id, this_ride.type, this_ride.date, this_ride.time, this_ride.meetup_location, this_ride.destination, this_ride.pace, this_ride.description)

        logger.log(logging.INFO, f"Ride added by user {update.effective_user.id}: \n{this_ride}")

        this_ride = None

        return ConversationHandler.END

    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.log(logging.DEBUG, f"Ride creation cancelled by user {update.effective_user.id}")
        await update.message.reply_text("Ride creation cancelled.")
        return ConversationHandler.END

ride_add_conv_handler = ConversationHandler(
        name="add_ride_handler",
        entry_points=[CommandHandler("add_ride", Ride_Helper_Functions.add_ride)],
        states= {
            Ride_Helper_Functions.TYPE: [MessageHandler(filters.Regex(regex_all), Ride_Helper_Functions.store_type_ask_date)],
            Ride_Helper_Functions.DATE: [MessageHandler(filters.Regex(regex_all), Ride_Helper_Functions.store_date_ask_time)],
            Ride_Helper_Functions.TIME: [MessageHandler(filters.Regex(regex_all), Ride_Helper_Functions.store_time_ask_meetup)],
            Ride_Helper_Functions.MEETUP: [MessageHandler(filters.Regex(regex_all), Ride_Helper_Functions.store_meetup_ask_destination)],
            Ride_Helper_Functions.DESTINATION: [MessageHandler(filters.Regex(regex_all), Ride_Helper_Functions.store_destination_ask_pace)],
            Ride_Helper_Functions.PACE: [MessageHandler(filters.Regex(regex_all), Ride_Helper_Functions.store_pace_ask_description)],
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
    - pace
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
        ["Destination", "Description"],
        ["Pace", "Cancel"]
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

        await update.message.reply_text("Enter the ID of the ride to modify")
        return Ride_Modify_Functions.ACTION
    
    async def select_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global this_mod

        if update.message.text == "/cancel":
            await update.message.reply_text("Ride modification cancelled.")
            logger.log(logging.DEBUG, f"Ride modification cancelled by user {update.effective_user.id}")
            return ConversationHandler.END
        
        this_mod = ModifyRideMemory()

        session = db.Session(db_creds)

        this_mod.set_ride(session.get_ride_by_id(update.message.text))

        if this_mod.get_ride().__str__() == None:
            await update.message.reply_text("Invalid ride. Please select a ride using its ID.")
            logger.log(logging.DEBUG, f"Invalid ride selected by user {update.effective_user.id}")
            return Ride_Modify_Functions.SELECT
        
        logger.log(logging.DEBUG, f"User {update.effective_user.id} selected ride: {this_mod.get_ride()}")
        
        await update.message.reply_text(f"Selected ride:\n{this_mod.get_ride()}\n\nSelect an action to perform on this ride", 
                                        reply_markup=ReplyKeyboardMarkup([["Modify", "Delete"]],
                                                                         one_time_keyboard=True, 
                                                                         input_field_placeholder="Select an action"))
        return Ride_Modify_Functions.READACTION
    
    async def read_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text == "/cancel":
            await update.message.reply_text("Ride modification cancelled.")
            logger.log(logging.DEBUG, f"Ride modification cancelled by user {update.effective_user.id}")
            return ConversationHandler.END

        if update.message.text == "Modify":
            logger.log(logging.DEBUG, f"User {update.effective_user.id} selected Modify")
            await update.message.reply_text("Select parameter to modify",
                                            reply_markup=ReplyKeyboardMarkup(Ride_Modify_Functions.mod_options_keyboard,
                                                                             one_time_keyboard=True,
                                                                            input_field_placeholder="Select a parameter to modify"))
            return Ride_Modify_Functions.MODOPTIONS
        elif update.message.text == "Delete":
            logger.log(logging.DEBUG, f"User {update.effective_user.id} selected Delete")
            yesno_keyboard = [["Yes", "No"]]
            await update.message.reply_text("Are you sure you want to delete this ride? (yes/no)",
                                            reply_markup=ReplyKeyboardMarkup(yesno_keyboard,
                                                                             one_time_keyboard=True,
                                                                             input_field_placeholder="yes/no"))
            return Ride_Modify_Functions.DELETE
        else:
            await update.message.reply_text("Invalid action. Please select an action from the list.")
            logger.log(logging.DEBUG, f"Invalid action selected by user {update.effective_user.id}")
            return Ride_Modify_Functions.ACTION
        
    async def mod_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text == "/cancel":
            await update.message.reply_text("Ride modification cancelled.")
            return ConversationHandler.END

        if update.message.text not in ["Type", "Date", "Time", "Meetup location", "Destination", "Pace", "Description", "Cancel"]:
            await update.message.reply_text("Invalid option. Please select a valid option from the list.")
            logger.log(logging.DEBUG, f"Invalid modifiction option selected by user {update.effective_user.id}")
            return Ride_Modify_Functions.MODOPTIONS
        
        global this_mod
        this_mod.set_field(update.message.text)

        if(update.message.text == "Cancel"):
            await update.message.reply_text("Ride modification cancelled.")
            return ConversationHandler.END

        logger.log(logging.DEBUG, f"User {update.effective_user.id} selected {this_mod.get_field()} to modify")

        await update.message.reply_text(f"Enter new value for {update.message.text}")
        return Ride_Modify_Functions.MODIFY
    
    async def modify_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text == "/cancel":
            await update.message.reply_text("Ride modification cancelled.")
            return ConversationHandler.END

        global this_mod
        this_mod.set_new_value(update.message.text)

        session = db.Session(db_creds)

        try:
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
            elif this_mod.get_field() == "Pace":
                session.update_ride(this_mod.get_ride().id, "pace", this_mod.get_new_value())
            elif this_mod.get_field() == "Description":
                session.update_ride(this_mod.get_ride().id, "description", this_mod.get_new_value())
        except ValueError:
            await update.message.reply_text("Invalid value. Please enter a valid value.")
            return Ride_Modify_Functions.MODIFY

        logger.log(logging.DEBUG, f"User {update.effective_user.id} modified {this_mod.get_field()} to {this_mod.get_new_value()}")

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

class Ride_Upload_Functions:
    async def upload_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.log(logging.DEBUG, "Upload ride command called")

        # check if the user is in a group chat
        if update.effective_chat.type == "group" or update.effective_chat.type == "supergroup":
            await update.message.reply_text("This command can only be used in a private chat.")
            logger.log(logging.INFO, f"User {update.effective_user.id} attempted to use command upload_ride in a group chat")
            return ConversationHandler.END

        # make sure the user is an admin
        is_admin = await utils.is_admin(update.effective_user)
        if not is_admin:
            logger.info(f"Unauthorized access to command upload_ride by user {update.effective_user.id}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You are not authorized to use this command.")
            return ConversationHandler.END

        await update.message.reply_text("Upload a ride file")
        return 1
    
    async def upload_ride_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text == "/cancel":
            await update.message.reply_text("Ride upload cancelled.")
            return ConversationHandler.END

        if not update.message.document:
            await update.message.reply_text("Invalid file. Please upload a file.")
            return ConversationHandler.END

        try:
            await update.message.reply_text(f"Downloading file {update.message.document.file_name}")
            await utils.download_ride(context, update.message.document.file_id, update.message.document.file_name, update.effective_user.id)
            await update.message.reply_text(f"File {update.message.document.file_name} downloaded.")
        except Exception as e:
            await update.effective_chat.send_message(f"Error downloading file: {e}\n\nPlease run the command again or contact the bot maintainer.")
            logger.log(logging.ERROR, f"Error downloading file: {e}")
            return ConversationHandler.END

        return ConversationHandler.END
    
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Ride upload cancelled.")
        return ConversationHandler.END
    
upload_ride_conv_handler = ConversationHandler(
        name="upload_ride_handler",
        entry_points=[CommandHandler("upload_ride", Ride_Upload_Functions.upload_ride)],
        states = {
            1: [MessageHandler(filters.ALL, Ride_Upload_Functions.upload_ride_file)]
        },
        fallbacks=[CommandHandler("cancel", Ride_Upload_Functions.cancel)]
    )