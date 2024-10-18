from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
import roy_counter
import requests

TEST_MODE = False

def longest_line(str):
    lines = str.split("\n")
    max = 0
    for line in lines:
        max = len(line) if len(line) > max else max
    return max

def generate_message_img(message, user, avatar, color, secret=False):
    
    x = (longest_line(message) * 18) + 234 if ((longest_line(message) * 16) + 234) >= 750 else 750 # 20px for each character of the longest line in the message, plus padding
    y = (message.count("\n") * 40) + 182 # 40px for each new line in a message
    
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
    draw.font = ImageFont.truetype("./font/ggsansRegular.ttf", size=32)
    draw.text((162, 86), message, fill=(219,222,225))

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
    generate_message_img("Roy\nMilton\nB-a-ke-r", "Hoeless Headless Horseman", "https://cdn.discordapp.com/avatars/231186156757319680/109460aae45aef3221e7ebced37b3090.webp?size=128", None)