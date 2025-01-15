import discord
import requests
import emoji
import os

def save_emoji_image(emoji_id, client):
    assert type(emoji_id) == int, "emoji_id must be a valid discord emoji id integer"
    assert client != None, "client must not be None"
    
    emoji = client.get_emoji(emoji_id)
    ext = emoji.url[-3:]

    if os.path.exists(f"./emojis/{emoji_id}.{ext}"):
        return ext
    else:
        data = requests.get(emoji.url)

        if data.ok:
            with open(f"./emojis/{emoji_id}.{ext}", "wb") as file:
                file.write(data.content)
            return ext
        else:
            print(f"Unable to download emoji from {emoji.url}")
            return None

def emoji_image(unicode_emoji):
    codepoint = "-".join(f"{ord(c):x}" for c in unicode_emoji)
    path = "./unicode_emojis/"
    return f"{path}{codepoint}.png"