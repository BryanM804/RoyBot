from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
import roy_counter
import numpy
import requests

def longest_line(str):
    lines = str.split("\n")
    max = 0
    for line in lines:
        max = len(line) if len(line) > max else max
    return max

def generate_message_img(message, user, avatar, color):
    
    x = (longest_line(message) * 8) + 117 if ((longest_line(message) * 8) + 117) >= 375 else 375 # 8px for each character of the longest line in the message, plus padding
    y = (message.count("\n") * 21) + 91 # 21px for each new line in a message
    
    # Mode, size, color
    message_img = Image.new("RGBA", (x, y), (49,51,56))

    # Create cropped avatar image
    square_avatar_img = Image.open(BytesIO(requests.get(avatar).content))
    mask = Image.new("L", square_avatar_img.size, 0)
    circle_draw = ImageDraw.Draw(mask)
    circle_draw.pieslice([(0, 0), square_avatar_img.size], 0, 360, fill=255)
    mask_arr = numpy.array(mask)
    avatarr = numpy.array(square_avatar_img)
    avatar_img = Image.fromarray(numpy.dstack((avatarr, mask_arr))).resize((41, 41))

    # Draw user avatar
    message_img.paste(avatar_img, (25, 25), mask=avatar_img)

    # Draw username text
    draw = ImageDraw.Draw(message_img)
    draw.font = ImageFont.truetype("./font/ggsansMedium.ttf", size=16)
    draw.text((81, 23), user, (color.r, color.g, color.b))

    # Draw time string
    current_time = datetime.now().strftime("%I:%M %p")
    if datetime.now().hour < 10 or (datetime.now().hour > 12 and datetime.now().hour < 22):
        current_time = current_time[1:]
    draw.font = ImageFont.truetype("./font/ggsansRegular.ttf", size=10)
    draw.text(((81 + len(user) * 8), 29), f"Today at {current_time}", fill=(148,155,164))

    # Draw main message text:
    draw.font = ImageFont.truetype("./font/ggsansRegular.ttf", size=16)
    draw.text((81, 43), message, fill=(219,222,225))

    #Resize
    message_img = message_img.resize((int(x * 1.5), int(y * 1.5)))

    # Save image
    with open(f"/mnt/2tbdrive/projects/RoyBot/message-imgs/roy-{roy_counter.roy_count}.png", "wb") as img_file:
        message_img.save(img_file)

# generate_message_jpeg("Roy\nMilton\nBaker", "Hoeless Headless Horseman", "https://cdn.discordapp.com/avatars/154820680687288320/12cd0e649a75177dc9378c8a6631b397.webp?size=128", None)