from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
from emoji import EMOJI_DATA
import discord
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

# pinged names must be separated by \u200b in place of any spaces in the display name
def generate_message_img(message, user, avatar, color, pinged_names, custom_emoji_ids, secret=False, client=None):

    # Add newlines to text that is too long
    words = message.split(" ")
    message = ""
    len_msg = ""
    message_strs = []
    emoji_len_modifier = 0
    line_count = 0
    for word in words:
        # Split words that are pings or emojis into separate strings
        if word in custom_emoji_ids or word in pinged_names or word in EMOJI_DATA:
            message_strs.append(message)
            message_strs.append(word)
            message = ""
        else:
            message += word + " "
        
        if word not in custom_emoji_ids or client == None:
            len_msg += word + " "
        else:
            len_msg += ". "
            emoji_len_modifier += 36

        # Message line count increases every time the length hits 250
        if int(len(len_msg) / 250) > line_count:
            message += "\n"
            len_msg += "\n"
            line_count += 1
    message_strs.append(message)

    # Make a throw away draw to get the text length for the message image size
    gdraw = ImageDraw.Draw(Image.new("L", (10, 10), 255))
    gdraw.font = ImageFont.truetype("./font/ggsansRegular.ttf", size=32)

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
    draw.font = ImageFont.truetype("./font/ggsansMedium.ttf", size=32)
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
        if st in custom_emoji_ids or st in EMOJI_DATA:
            emoji = None
            # Draw an emoji
            if st in EMOJI_DATA:
                emoji = Image.open(emoji_manager.emoji_image(st)).convert("RGBA")
            elif client != None:
                ext = emoji_manager.save_emoji_image(int(st), client)
                emoji = Image.open(f"./emojis/{st}.{ext}").convert("RGBA")
            else:
                draw.font = ImageFont.truetype("./font/ggsansRegular.ttf", size=32)
                draw.text((x, y), st, fill=(219,222,225))

            if emoji != None:
                emojipx = emoji.load()
                ex, ey = emoji.size
                for pxx in range(ex):
                    for pxy in range(ey):
                        if emojipx[pxx, pxy][3] <= 10: # If the pixel in the emoji is mostly transparent set it to the background color
                            emojipx[pxx, pxy] = (49,51,56, 255) 
                emoji = emoji.resize((40, 40))

                message_img.paste(emoji, (int(x), int(y)))
                x += 42
                continue
        elif st in pinged_names:
            # Draw user ping with highlight
            st = st.replace("\u200B", " ")
            draw.font = ImageFont.truetype("./font/ggsansMedium.ttf", size=32)
            tl = draw.textlength(st, draw.font, font_size=32)
            hl_padding = 2
            # x1, y1, x2, y2
            hl_pos = (x - hl_padding, y - hl_padding, x + tl + hl_padding, y + 40 + hl_padding)
            draw.rectangle(hl_pos, fill=(60,66,112))

            draw.text((x, y), st, fill=(227,229,254))
        elif "\n" in st:
            # Draw Regular text with newlines
            draw.font = ImageFont.truetype("./font/ggsansRegular.ttf", size=32)
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
            draw.font = ImageFont.truetype("./font/ggsansRegular.ttf", size=32)
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
    generate_message_img("Test Message @roy 620295484635873300", "Test User", "https://cdn.discordapp.com/avatars/231186156757319680/109460aae45aef3221e7ebced37b3090.webp?size=128",
                          None, ["@roy"], ["620295484635873300"])