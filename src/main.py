import discord
import logging
from handlers import messages
from handlers import ready
from secret import secret_token

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
logger = logging.FileHandler(filename="logs/discord.log", encoding="utf-8", mode="w")

@client.event
async def on_ready():
    await ready.handle_ready(client)

@client.event
async def on_message(message):
    await messages.handle_message(client, message)

client.run(secret_token.secret_token, log_handler=logger)