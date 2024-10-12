import os
import re
import discord
import roy_counter
import image_generator
import image_circler

async def getFilePath():
    for file in os.listdir("/mnt/2tbdrive/projects/RoyBot/message-imgs"):
        if "roy" not in file:
            return file

async def handle_message(client, message):
    if message.author == client.user:
        return

    original = message.content
    contents = original.lower().replace(" ", "")
    contents = re.sub(r"[^(a-z|A-Z)]", "", contents)

    if "roy" in contents:
        image_generator.generate_message_jpg(original, message.author.display_name, message.author.display_avatar.url)
        try:
            message_path = await getFilePath()
            message_path = "/mnt/2tbdrive/projects/RoyBot/message-imgs/" + message_path

            image_circler.circle_roy(message_path)
            roy_counter.inc_count(roy_counter.roy_count)

            new_path = f"/mnt/2tbdrive/projects/RoyBot/message-imgs/roy-{roy_counter.roy_count}.jpeg"
            os.rename(message_path, new_path)

            await message.reply(f"# 🚨ROY ALERT🚨\nroy #{roy_counter.roy_count}", file=discord.File(new_path))
        except Exception as e:
            print(e)
            roy_counter.inc_count(roy_counter.roy_count)
            await message.reply(f"# 🚨ROY ALERT🚨\nroy #{roy_counter.roy_count}")
        await message.add_reaction("🇷")
        await message.add_reaction("🇴")
        await message.add_reaction("🇾")
        return