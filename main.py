import logging
import time
import os

from telegram import (
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
)

import simple_commands
import admin_commands
import data
import db
import environment_handler

commands_descriptions = data.commands_descriptions

prog_start_time = time.time()
log_filename = f"./logs/Log-{time.strftime('%Y-%m-%d-%H-%M-%S')}.log"
log_format = "%(asctime)s,%(name)s,%(levelname)s,%(message)s" # Logs readable as CSV because I am special

# set higher logging level for httpx to avoid all GET and POST requests being logged
# idk what this does but the example used it and it works so I'm keeping it
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore.http11").setLevel(logging.WARNING)
logging.getLogger("telegram.ext.ExtBot").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

deployment, token, db_creds = environment_handler.get_env_vars()

db_creds = db.DB_Credentials(
    host=os.getenv("postgres_host", None),
    user=os.getenv("postgres_user", None),
    password=os.getenv("postgres_pass", None),
    database=os.getenv("postgres_db", None)
)

commands = {
    "nosedive": simple_commands.nosedive,
    "rules": simple_commands.rules,
    "links": simple_commands.links,
    "codes": simple_commands.codes,
    "helmet": simple_commands.helmet,
    "help": simple_commands.help,
    "pads": simple_commands.pads,
    "i2s": simple_commands.i2s
}

admin_commands = {
    "test_admin": admin_commands.test_admin,
    "announce": admin_commands.announce
}

def main():
    app = Application.builder().token(token).build()
    for i in commands: # Added programatically to make commands able to be referenced
        app.add_handler(CommandHandler(i, commands[i]))
    for i in admin_commands:
        app.add_handler(CommandHandler(i, admin_commands[i]))

    app.add_handler(ChatMemberHandler(simple_commands.welcome, ChatMemberHandler.CHAT_MEMBER))

    # TODO: make commands show when you type "/" in chat

    app.run_polling(allowed_updates=Update.ALL_TYPES)

main()