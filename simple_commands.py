import logging

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

logger = logging.getLogger(__name__)

"""
This file contains simple commands that provide a canned response, with no secondary effects and no database interaction.
No database interaction until I stop being lazy and implement it.
Eventually all of these responses should pull dynamically from the database to allow updates without code changes.
"""

responses = { # Eventually, this will all be pulled from a database editable on the website. For now, it's hardcoded. Because I am lazy.
    "welcome": "Welcome to UIUC PEV! Do /rules to check the rules of the group, and /help to see other commands!",
    "rules_header": "The rules of this group are generally pretty simple. They are:",
    "rules": """            1. Wear a helmet\n 
            2. WEAR A HELMET\n
            3. Follow the rules of the road\n
            4. Keep a safe riding distance\n
            5. Stagger while riding\n
            6. Don't wear loose clothes that might get caught\n
            7. Be careful where you point your flashlight\n
            8. Know your limits, and ride within them\n
            9. Communicate with your fellow riders\n
            10. Have fun!
            """, # 3 tabs at the beginning keeps the alignment at bay

    "nosedive": 'ayy lmao\nhttps://www.youtube.com/watch?v=kc6IEVV9mp0', # stolen directly from ChiPEV
    "links": "All of our links can be found [here](https://linktr.ee/UIUCPEV)",
    "codes": "Discount codes are stolen from ChiPEV, and can be found [here](https://docs.google.com/spreadsheets/d/1QTMuWO8k5719MeBt535rA_kPvSEVmiTI3wVA9Bcwu5g/edit?usp=sharing)",
    "helmet": """[I LOVE HELMETS](https://www.youtube.com/watch?v=b9yL5usLFgY)\n
            Make sure you wear a good helmet\!\n
            Some good brands:\n
            [Bern](http://www.bernunlimited.com/)\n
            [Zeitbike](https://www.zeitbike.com/collections/helmets/)\n
            [Thousand](https://www.explorethousand.com/)\n
            [Ruroc](https://www.ruroc.com/en/)
            """
}


async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    logger.info(f"Sending message: {message}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.MARKDOWN_V2)
    return

async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Links command called")
    await send_message(update, context, responses["links"])

async def nosedive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Nosedive command called")
    await send_message(update, context, responses["nosedive"])
    return

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Rules command called")

    rules_msg = responses["rules_header"] + "\n\n" + responses["rules"]
    await send_message(update, context, rules_msg)

    return

async def helmet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Helmet command called")
    await send_message(update, context, responses["helmet"])
    return

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Help command called")
    help_msg = "Here are the commands you can use:\n"
    for i in responses: # TODO: Make this filter by what the user can actually do
        help_msg += f"/{i} - {responses[i]}\n"
    await send_message(update, context, help_msg)
    return

async def pads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Pads command called")
    await send_message(update, context, "Pads are important! Make sure you wear them!")
    return

async def codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Codes command called")
    await send_message(update, context, responses["codes"])
    return