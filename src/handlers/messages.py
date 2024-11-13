import os
import re
import requests
import json
import discord
import roy_counter
from pytenor import Tenor
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
    
    # Search image attachments for roy
    for att in message.attachments:
        if "image" in att.content_type:
            ext = att.content_type[6:]
            await att.save(f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count + 1}.{ext}", use_cached=True)
            if ext == "gif":
                if image_circler.circle_word_gif(f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count + 1}.{ext}", "roy", success_dest=f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count + 1}.png"):
                    roy_counter.inc_count(roy_counter.roy_count)
                    await message.reply(f"# 🚨ROY ALERT🚨\nroy #{roy_counter.roy_count}", file=discord.File(f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count}.jpeg"))
            elif image_circler.circle_word(f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count + 1}.{ext}", "roy"):
                roy_counter.inc_count(roy_counter.roy_count)
                await message.reply(f"# 🚨ROY ALERT🚨\nroy #{roy_counter.roy_count}", file=discord.File(f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count}.{ext}"))

    await secret_box.secret_check(client, message)

    original = message.content
    contents = original.lower().replace(" ", "")
    contents = re.sub(r"[^(a-z|A-Z)]", "", contents)

    if "httpstenorcom" in contents:
        gifid = re.sub(r"[^(0-9)]", "", message.content)

        results = json.loads(requests.get("https://tenor.googleapis.com/v2/posts?ids=%s&key=%s" % (gifid, "AIzaSyDWjZozo-pLXf4Zy6PK_ti75MCP0WVs7Fg")).content)
        data = requests.get(results["results"][0]["media_formats"]["mediumgif"]["url"]).content

        with open(f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count + 1}.gif", "wb") as download:
            download.write(data)

        if image_circler.circle_word_gif(f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count + 1}.gif", "roy", success_dest=f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count + 1}.jpeg") or image_circler.circle_word_gif(f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count + 1}.gif", "ctt", success_dest=f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count + 1}.jpeg"):
                    roy_counter.inc_count(roy_counter.roy_count)
                    await message.reply(f"# 🚨ROY ALERT🚨\nroy #{roy_counter.roy_count}", file=discord.File(f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count}.jpeg"))
    elif "roy" in contents:
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