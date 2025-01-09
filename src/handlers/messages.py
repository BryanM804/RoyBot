import os
import re
import requests
import json
import discord
import roy_counter
import multiprocessing
from pytenor import Tenor
from secret import secret_box
import image_generator
import image_circler

q = multiprocessing.Queue()

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
            path = f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count + 1}-{message.id}.{ext}"
            await att.save(path, use_cached=True)
            
            if ext == "gif":
                p = multiprocessing.Process(target=check_gif, args=(q, path, message.id, message.channel.id))
                p.start()
            else:
                p = multiprocessing.Process(target=check_image, args=(q, path, message.id, message.channel.id))
                p.start()

    await secret_box.secret_check(client, message)

    original = message.content
    contents = original.lower().replace(" ", "")
    contents = re.sub(r"[^(a-z|A-Z)]", "", contents)

    if "httpstenorcom" in contents or "httpscdndiscordappcomattachments" in contents:
        path = f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count + 1}-{message.id}.gif"

        if "httpstenorcom" in contents:
            gifid = re.sub(r"[^(0-9)]", "", message.content)

            results = json.loads(requests.get("https://tenor.googleapis.com/v2/posts?ids=%s&key=%s" % (gifid, "AIzaSyDWjZozo-pLXf4Zy6PK_ti75MCP0WVs7Fg")).content)
            data = requests.get(results["results"][0]["media_formats"]["mediumgif"]["url"]).content

            with open(path, "wb") as download:
                download.write(data)
        else:
            data = requests.get(original.replace("cdn.discordapp.com", "fixcdn.hyonsu.com")).content

            with open(path, "wb") as download:
                download.write(data)

        p = multiprocessing.Process(target=check_gif, args=(q, path, message.id, message.channel.id))
        p.start()

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
    
def check_gif(queue, path, id, cid):
    res = image_circler.circle_gif(path, "roy")
    if res[0]:
        os.rename(res[1], f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count}.png")
        queue.put((id, f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count}.png", cid))
        print("queue populated")

def check_image(queue, path, id, cid):
    word_res = image_circler.circle_word(path, "roy")
    face_res = image_circler.circle_face(path)
    if word_res[0] or face_res[0]:
        queue.put((id, path, cid))
        print("queue populated")