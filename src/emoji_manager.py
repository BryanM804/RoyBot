import requests
import os
import emoji

REGIONAL_INDICATORS = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇷", "🇻", "🇼", "🇽", "🇾", "🇿"]

def save_emoji_image(emoji_id, client):
    assert type(emoji_id) == int, "emoji_id must be a valid discord emoji id integer"
    assert client != None, "client must not be None"
    
    emoji = client.get_emoji(emoji_id)

    if type(emoji) == None:
        print(f"Unable to get emoji {emoji_id}")
        return

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

    if os.path.exists(f"{path}{codepoint}.png"):
        return f"{path}{codepoint}.png"
    elif os.path.exists(f"{path}{codepoint}-fe0f.png"):
        # I don't know what fe0f is but rarely the emojis that need it don't get it as the last part of the codepoint
        return f"{path}{codepoint}-fe0f.png"
    else:
        print(f"File {path}{codepoint}.png does not exist.")

# Separates unicode emojis out of strings and returns the list as the first element of a tuple
# message and len_msg are also passed back if present
def separate_emoji(word, message="", len_msg=None):
    # This is annoying to read, some unicode emojis are multiple characters and some aren't
    # This will separate them in case there are mulitple without spaces in between
    initmsg = message
    was_emoji = False
    message_strs = []

    for c in word:
        if was_emoji:
            if (message + c) in emoji.EMOJI_DATA:
                message += c
                continue
            else:
                message_strs.append(message)
                message = ""
                if len_msg != None: len_msg += ".."
                was_emoji = False

        if c in emoji.EMOJI_DATA or c in REGIONAL_INDICATORS:
            if not was_emoji and message != "" and message != " ":
                message_strs.append(message)
                message = ""
            was_emoji = True 
            message += c   
        else:
            message += c
            if len_msg != None: len_msg += c
    if was_emoji or initmsg == "":
        message_strs.append(message)
        message = ""
        if len_msg != None and was_emoji: 
            len_msg += ".."
    
    if len_msg != None:
        return (message_strs, message, len_msg)
    else:
        return (message_strs, message)