import os
import discord
import roy_counter
import image_generator
import image_circler

async def getFilePath():
    for file in os.listdir("/mnt/2tbdrive/projects/RoyBot/message-imgs"):
        return f"/mnt/2tbdrive/projects/RoyBot/message-imgs/{file}"

async def handle_message(client, message):
    if message.author == client.user:
        return

    original = message.content
    contents = original.lower().replace(" ", "")

    if "roy" in contents:
        image_generator.generate_message_jpg(original, message.author.display_name, message.author.display_avatar.url)
        roy_counter.inc_count(roy_counter.roy_count)
        try:
            message_path = await getFilePath()
            image_circler.circle_roy(message_path)
            await message.reply(f"@here roy #{roy_counter.roy_count}", file=discord.File(message_path))
            os.remove(message_path)
        except Exception:
            await message.reply(f"@everyone roy #{roy_counter.roy_count}")
        await message.add_reaction("🇷")
        await message.add_reaction("🇴")
        await message.add_reaction("🇾")
        return