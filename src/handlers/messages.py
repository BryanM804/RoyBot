import os
import re
import discord
import roy_counter
from secret import secret_box
import image_generator
import image_circler

async def getFilePath():
    for file in os.listdir("/mnt/2tbdrive/projects/RoyBot/message-imgs"):
        if "roy" not in file:
            return file

async def handle_message(client, message):
    if message.author == client.user:
        return

    await secret_box.secret_check(client, message)

    original = message.content
    contents = original.lower().replace(" ", "")
    contents = re.sub(r"[^(a-z|A-Z)]", "", contents)

    if "roy" in contents:
        roy_counter.inc_count(roy_counter.roy_count)
        try:
            # image_loader.get_web_image(original, message.author.display_name, message.author.display_avatar.url, message.author.color)

            image_generator.generate_message_img(original, message.author.display_name, message.author.display_avatar.url, message.author.color)
            image_circler.circle_word(f"/mnt/2tbdrive/projects/RoyBot/message-imgs/roy-{roy_counter.roy_count}.png", "roy")

            await message.reply(f"# 🚨ROY ALERT🚨\nroy #{roy_counter.roy_count}", file=discord.File(f"/mnt/2tbdrive/projects/RoyBot/message-imgs/roy-{roy_counter.roy_count}.png"))
        except Exception as e:
            print(e)
            await message.reply(f"# 🚨ROY ALERT🚨\nroy #{roy_counter.roy_count}")
        await message.add_reaction("🇷")
        await message.add_reaction("🇴")
        await message.add_reaction("🇾")
        return