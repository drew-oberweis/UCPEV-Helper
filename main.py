import logging
import time
import os
import sys

from telegram import (
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
    filters,
    ConversationHandler
)

import user_commands
import admin_commands
import data
import db
import environment_handler
import custom_handlers as c_handlers
import utils
from sheets_interface import refresh_token

prog_start_time = time.time()
log_filename = f"./logs/Log-{time.strftime('%Y-%m-%d-%H-%M-%S')}.log"
log_format = "%(asctime)s,%(name)s,%(levelname)s,%(message)s" # Logs readable as CSV because I am special

# set higher logging level for httpx to avoid all GET and POST requests being logged

extraLogLevel = logging.WARNING

logging.getLogger("httpx").setLevel(extraLogLevel)
logging.getLogger("httpcore.http11").setLevel(extraLogLevel)
logging.getLogger("telegram.ext.ExtBot").setLevel(extraLogLevel)
logging.getLogger("telegram.ext.Application").setLevel(extraLogLevel)
logging.getLogger("httpcore.connection").setLevel(extraLogLevel)
logging.getLogger("telegram.ext.Updater").setLevel(extraLogLevel)
logging.getLogger("telegram.ext.ConversationHandler").setLevel(extraLogLevel)

logger = logging.getLogger(__name__)

token, db_creds = environment_handler.get_env_vars()

db_creds = db.DB_Credentials(
    host=os.getenv("postgres_host", None),
    user=os.getenv("postgres_user", None),
    password=os.getenv("postgres_pass", None),
    database=os.getenv("postgres_db", None)
)

log_level = environment_handler.get_log_level()
logging.basicConfig(format=log_format, level=log_level, stream=sys.stdout)

environment_handler.generate_google_creds()

commands_map = {
    "nosedive": user_commands.nosedive,
    "rules": user_commands.rules,
    "links": user_commands.links,
    "codes": user_commands.codes,
    "helmet": user_commands.helmet,
    "help": user_commands.help,
    "pads": user_commands.pads,
    "i2s": user_commands.i2s,
    "rides": user_commands.rides,
}

admin_commands_map = {
    "test_admin": admin_commands.test_admin,
    "announce": admin_commands.announce,
    "make_ride_poll": admin_commands.make_ride_poll,
}

def main():
    app = Application.builder().token(token).build()

    for i in commands_map:
        app.add_handler(CommandHandler(i, commands_map[i]))
    for i in admin_commands_map:
        app.add_handler(CommandHandler(i, admin_commands_map[i]))

    app.add_handler(ChatMemberHandler(user_commands.welcome, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.ALL ,c_handlers.on_message))

    app.job_queue.run_repeating(refresh_token, interval=60*60*24)

    command_list = utils.output_telegram_autocomplete()
    # write the command list to a file
    with open("commands.txt", "w") as f:
        f.write(command_list)

    app.run_polling(allowed_updates=Update.ALL_TYPES)

main()