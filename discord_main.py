import discord
import logging
import time
import sys

import environment_handler

logger = logging.getLogger(__name__)

logger.info("Logging initialized.")

def main():

    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logger.info(f"Logged into discord as {client.user} (ID: {client.user.id})")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith("!hello"):
            await message.channel.send("Hello! I'm a bot.")

    client.run('NzU5NjAxMzI2NDI1NjM2ODY0.GgjTAP.Mrw9iWO98kX0jWKsT0FPECFxkuHdPEfpmsHlpw')