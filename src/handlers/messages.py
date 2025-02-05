import os
import re
import requests
import json
import discord
import roy_counter
import threading
import queue
from secret import secret_box
import image_generator
import image_circler

q = queue.Queue()

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
                t = threading.Thread(target=check_gif, args=(q, path, message.id, message.channel.id))
                t.start()
            else:
                t = threading.Thread(target=check_image, args=(q, path, message.id, message.channel.id))
                t.start()

    original = message.content
    pings = re.findall(r"<@\d+>", original)
    roy_pinged = False
    pinged_names = []

    if "@everyone" in original:
        pinged_names.append("everyone")
    if "@here" in original:
        pinged_names.append("here")
    if message.guild:
        for ping in pings:
            id = re.sub(r"[^\d]+", "", ping)
            roy_pinged = True if int(id) == 112236423473573888 else roy_pinged
            # Replaces spaces in display names with 0 width spaces so they aren't split later in the image generator
            name = message.guild.get_member(int(id)).display_name.replace(" ", "\u200B")
            pinged_names.append(f"@{name}")
            original = original.replace(ping, f"@{name}")

    emojis = re.findall(r"<a?:[a-z|A-Z]+:\d+>", original)
    emoji_ids = []
    for emoji in emojis:
        id = re.sub(r"<a?:([a-z]|[A-Z])+:", "", emoji)
        id = id[:-1]
        emoji_ids.append(id)
        original = original.replace(emoji, id)

    await secret_box.secret_check(client, message, pinged_names, emoji_ids)
        
    contents = original.lower().replace(" ", "")
    contents = re.sub(r"[^(a-z|A-Z)]", "", contents)

    if "httpstenorcom" in contents or "cdndiscordappcomattachments" in contents:
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

        t = threading.Thread(target=check_gif, args=(q, path, message.id, message.channel.id))
        t.start()

    elif "roy" in contents or roy_pinged:
        roy_counter.inc_count(roy_counter.roy_count)
        try:
            # image_loader.get_web_image(original, message.author.display_name, message.author.display_avatar.url, message.author.color)

            image_generator.generate_message_img(original, message.author.display_name, message.author.display_avatar.url, message.author.color, pinged_names, emoji_ids, client=client)
            if roy_pinged and message.guild:
                image_circler.circle_word(f"/mnt/2tbdrive/projects/RoyBot/message-imgs/roy-{roy_counter.roy_count}.png", f"@{message.guild.get_member(112236423473573888).display_name}")
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
        #os.rename(res[1], f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count}.png")
        os.rename(res[1], f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count}.gif")
        #queue.put((id, f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count}.png", cid))
        queue.put((id, f"/mnt/2tbdrive/projects/RoyBot/downloads/attachment-{roy_counter.roy_count}.gif", cid))
        print("queue populated")

def check_image(queue, path, id, cid):
    word_res = image_circler.circle_word(path, "roy")
    face_res = image_circler.circle_face(path)
    if word_res[0] or face_res[0]:
        queue.put((id, path, cid))
        print("queue populated")