from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
from emoji import EMOJI_DATA
import emoji_manager
import roy_counter
import requests
import argparse

parser = argparse.ArgumentParser(description="Test mode to generate test image")
parser.add_argument("--test_mode", type=bool, default=False)

# Bot will not save images correctly if TEST_MODE is True
args = parser.parse_args()
TEST_MODE = args.test_mode

def longest_line(st):
    lines = st.split("\n")
    max = ""
    for line in lines:
        max = line if len(line) > len(max) else max
    return max

# pinged names must be separated by \u200b in place of any spaces in the display name and be in form of "@Display Name"
# Custom emojis must only be the emoji's numerical ID and each occurence must be in the custom_emoji_ids list in order of appearence
def generate_message_img(message, user, avatar, color, pinged_names, custom_emoji_ids, secret=False, client=None):
    ggsansregular = ImageFont.truetype("./font/ggsansRegular.ttf", size=32)
    ggsansmedium = ImageFont.truetype("./font/ggsansMedium.ttf", size=32)
    segoeuiemoji = ImageFont.truetype("./font/seguiemj.ttf", size=32)
    words = message.split(" ")
    message = ""
    len_msg = ""
    message_strs = []
    line_count = 0
    emoji_i = 0
    name_i = 0

    for word in words:
        # Separate pinged names and emojis from plain text
        if len(custom_emoji_ids) > emoji_i or len(pinged_names) > name_i:
            if message != "":
                message_strs.append(message)
            message = ""
            while (len(custom_emoji_ids) > emoji_i and custom_emoji_ids[emoji_i] in word) or (len(pinged_names) > name_i and pinged_names[name_i] in word):
                e_pos = word.find(custom_emoji_ids[emoji_i]) if len(custom_emoji_ids) > emoji_i else -1
                n_pos = word.find(pinged_names[name_i]) if len(pinged_names) > name_i else -1

                if (n_pos < e_pos and n_pos != -1) or (e_pos == -1 and n_pos != -1):
                    # name appears first
                    message_strs.append(word[0:n_pos])
                    message_strs.append(pinged_names[name_i])
                    len_msg += word[0:n_pos]
                    # Simpler to use this function to add the length than it would be to mess with fonts and stuff later
                    _, _, len_msg = emoji_manager.separate_emoji(pinged_names[name_i], "", len_msg)
                    word = word[n_pos + len(pinged_names[name_i]):]
                    name_i += 1
                else:
                    # emoji appears first
                    message_strs.append(word[0:e_pos])
                    message_strs.append(custom_emoji_ids[emoji_i])
                    if client != None:
                        len_msg += ".."
                    else:
                        len_msg += word[0:e_pos] + custom_emoji_ids[emoji_i]
                    word = word[e_pos + len(custom_emoji_ids[emoji_i]):]
                    emoji_i += 1
        if word in EMOJI_DATA or word in emoji_manager.REGIONAL_INDICATORS:
            if message != "":
                message_strs.append(message)
            message_strs.append(word)
            message = ""
            len_msg += ".."
        else:
            # This will change if I think of a better way to split the original message apart
            elements, message, len_msg = emoji_manager.separate_emoji(word, message, len_msg)
            message_strs += elements
            message += " "
            len_msg += " "

        # Message line count increases every time the length hits 140
        # This usually makes the lines line up the same as they would on a 1080p fullscreen window
        if int(len(len_msg) / 140) > line_count:
            message += "\n"
            len_msg += "\n"
            line_count += 1
    if message != "" and message != " ":
        message_strs.append(message)

    if TEST_MODE: print(message_strs)

    # Make a throw away draw to get the text length for the message image size
    gdraw = ImageDraw.Draw(Image.new("L", (10, 10), 255))
    gdraw.font = ggsansregular

    # Emoji length modifier makes sure to add extra space for the emojis in the text
    emoji_len_modifier = longest_line(len_msg).count("..") * 30

    xlen = int(gdraw.textlength(longest_line(len_msg), gdraw.font, font_size=32) + 234 + emoji_len_modifier)
    x = xlen if xlen >= 750 else 750
    y = (len_msg.count("\n") * 40) + 182 # 40px for each new line in a message
    
    # Mode, size, color
    message_img = Image.new("RGBA", (x, y), (49,51,56))

    # Create cropped avatar image
    avatar_img = Image.open(BytesIO(requests.get(avatar).content)).convert("RGBA")
    mask = Image.new("L", avatar_img.size, 0)
    circle_draw = ImageDraw.Draw(mask)
    circle_draw.pieslice([(0, 0), avatar_img.size], 0, 360, fill=255)

    av_pixels = avatar_img.load()
    mask_pixels = mask.load()
    mh, mw = mask.size
    for y in range(mh):
        for x in range(mw):
            if mask_pixels[x, y] == 0 or av_pixels[x, y][3] <= 10: # If the pixel in the mask is black or the pixel in the avatar is mostly transparent
                av_pixels[x, y] = (49,51,56, 255) # Make the pixel in the avatar background color
                
    
    avatar_img = avatar_img.resize((82, 82))

    # Draw user avatar
    message_img.paste(avatar_img, (50, 50))

    # Draw username text
    draw = ImageDraw.Draw(message_img)
    draw.font = ggsansmedium
    draw.text((162, 46), user, (120, 120, 120)) if TEST_MODE else draw.text((162, 46), user, (color.r, color.g, color.b))

    # Draw time string
    offset = draw.textlength(user, draw.font, font_size=32)
    current_time = datetime.now().strftime("%I:%M %p")
    if datetime.now().hour < 10 or (datetime.now().hour > 12 and datetime.now().hour < 22):
        current_time = current_time[1:]
    draw.font = ImageFont.truetype("./font/ggsansRegular.ttf", size=20)
    draw.text(((180 + offset), 58), f"Today at {current_time}", fill=(148,155,164))

    # Draw main message text:
    x = 162
    y = 86
    for st in message_strs:
        if st in custom_emoji_ids or st in EMOJI_DATA or st in emoji_manager.REGIONAL_INDICATORS:
            emoji = None
            # Draw an emoji
            if st in EMOJI_DATA or st in emoji_manager.REGIONAL_INDICATORS:
                emoji = Image.open(emoji_manager.emoji_image(st)).convert("RGBA")
            elif client != None:
                ext = emoji_manager.save_emoji_image(int(st), client)
                if ext == None:
                    x += 42
                    continue
                emoji = Image.open(f"./emojis/{st}.{ext}").convert("RGBA")
            else:
                draw.font = ggsansregular
                draw.text((x, y), st, fill=(219,222,225))

            if emoji != None:
                emojipx = emoji.load()
                ex, ey = emoji.size
                for pxx in range(ex):
                    for pxy in range(ey):
                        if emojipx[pxx, pxy][3] <= 10: # If the pixel in the emoji is mostly transparent set it to the background color
                            emojipx[pxx, pxy] = (49,51,56, 255) 
                emoji = emoji.resize((39, 39))

                message_img.paste(emoji, (int(x), int(y)))
                x += 42
                continue
        elif st in pinged_names:
            # Draw user ping with highlight
            st = st.replace("\u200B", " ")
            
            elements, _ = emoji_manager.separate_emoji(st)
            print(elements)
            tl = 0
            for e in elements:
                if e in EMOJI_DATA:
                    tl += draw.textlength(e, segoeuiemoji, font_size=32)
                else:
                    tl += draw.textlength(e, ggsansmedium, font_size=32)
            hl_padding = 2
            # x1, y1, x2, y2
            hl_pos = (x - hl_padding, y - hl_padding, x + tl + hl_padding, y + 40 + hl_padding)
            draw.rectangle(hl_pos, fill=(60,66,112))
            
            for e in elements:
                if e in EMOJI_DATA:
                    draw.font = segoeuiemoji
                    draw.text((x, y + 8), e, embedded_color=True)
                else:
                    draw.font = ggsansmedium
                    draw.text((x, y), e, fill=(227,229,254))
                x += draw.textlength(e, draw.font, font_size=32)
            continue
        elif "\n" in st:
            # Draw Regular text with newlines
            draw.font = ggsansregular
            strs = st.split("\n")
            for sub_str in strs:
                draw.text((x, y), sub_str, fill=(219,222,225))
                x = 162
                y += 40
            x += draw.textlength(strs[-1], draw.font, font_size=32)
            y -= 40
            continue
        else:
            # Draw regular text
            draw.font = ggsansregular
            draw.text((x, y), st, fill=(219,222,225))
        x += draw.textlength(st, draw.font, font_size=32)


    # Save image
    if TEST_MODE:
        with open(f"/mnt/2tbdrive/projects/RoyBot/asdasdasd.png", "wb") as img_file:
            message_img.save(img_file, format="png")
    elif secret:
        with open(f"/mnt/2tbdrive/projects/RoyBot/message-imgs/secret.png", "wb") as img_file:
            message_img.save(img_file)
    else:
        with open(f"/mnt/2tbdrive/projects/RoyBot/message-imgs/roy-{roy_counter.roy_count}.png", "wb") as img_file:
            message_img.save(img_file)
    
if TEST_MODE:
    generate_message_img("", "Test User", "https://cdn.discordapp.com/avatars/231186156757319680/109460aae45aef3221e7ebced37b3090.webp?size=128",
                          None, [], [])