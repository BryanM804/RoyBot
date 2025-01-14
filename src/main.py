import discord
import logging
import asyncio
import roy_counter
from discord import TextChannel, abc
from image_circler import generate_roy_encoding
from handlers import messages
from handlers.messages import q
from handlers import ready
from secret import secret_token

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
logger = logging.FileHandler(filename="logs/discord.log", encoding="utf-8", mode="w")

def convert_channel(channel: abc.GuildChannel) -> TextChannel:
    if isinstance(channel, TextChannel):
        return channel

async def send_alert(cid, messageid, roy_num, file_path):
    channel = client.get_channel(int(cid))
    if channel == None:
        try:
            print(f"Could not find cached channel: {cid}, trying to fetch.")
            channel = await client.fetch_channel(int(cid))
            channel = convert_channel(channel)
            await channel.send(content=f"# 🚨ROY ALERT🚨\nroy #{roy_num}", reference=channel.get_partial_message(int(messageid)), file=discord.File(file_path))
        except Exception as e:
            print(f"Unable to find channel: {cid}\n{e}")
    else:
        await channel.send(content=f"# 🚨ROY ALERT🚨\nroy #{roy_num}", reference=channel.get_partial_message(int(messageid)), file=discord.File(file_path))

async def check_replies(queue):
    while True:
        res = await asyncio.to_thread(queue.get)
        roy_counter.inc_count(roy_counter.roy_count)
        c = roy_counter.roy_count
        await send_alert(res[2], res[0], c, res[1])

@client.event
async def on_ready():
    generate_roy_encoding()
    await ready.handle_ready(client)
    task = asyncio.create_task(check_replies(q))
    await task

@client.event
async def on_message(message):
    await messages.handle_message(client, message)

client.run(secret_token.secret_token, log_handler=logger)