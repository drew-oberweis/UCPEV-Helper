import discord
import logging
import time
import sys

import environment_handler
from utils import MessageQueue, Message

logger = logging.getLogger(__name__)

logger.info("Logging initialized.")

global queue

def main(q: MessageQueue = None):

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

        global queue
        queue = q

        if queue is None:
            logger.error("Message queue is not initialized.")
            return

        logger.debug(f"Received message: {message.content} from {message.author} in channel {message.channel}")

        if message.content.startswith("!hello"):
            await message.channel.send("Hello! I'm a bot.")

        msg_obj = Message()
        msg_obj.set_dest_platform("telegram")
        msg_obj.set_user(str(message.author))
        msg_obj.set_chat(str(message.channel))
        msg_obj.set_message(message.content)
        msg_obj.set_chat_id("telegram",message.channel.id)
        queue.add_message(msg_obj)

            

    client.run('NzU5NjAxMzI2NDI1NjM2ODY0.GgjTAP.Mrw9iWO98kX0jWKsT0FPECFxkuHdPEfpmsHlpw')