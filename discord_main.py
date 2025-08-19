import discord
import logging
import time
import sys

import environment_handler
from message_queue import MessageQueue, Message

logger = logging.getLogger(__name__)

logger.info("Logging initialized.")

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
            logger.debug("Ignoring own message.")
            return

        # ignore webhook messages
        if message.webhook_id is not None:
            logger.debug("Ignoring webhook message.")
            return

        if q is None:
            logger.error("Message queue is not initialized.")
            return

        logger.debug(f"Received message: {message.content} from {message.author.display_name} ({message.author.id}) in channel {message.channel}")

        msg_obj = Message()
        msg_obj.set_user(str(message.author.display_name))
        msg_obj.set_chat(str(message.channel))
        msg_obj.set_message(message.content)
        msg_obj.set_discord_topic_id(message.channel.id)
        q.add_message(msg_obj)

    client.run(environment_handler.get_discord_token())