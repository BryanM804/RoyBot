from roy_counter import roy_count
from discord import app_commands
import discord
import random
import os

def setup(tree: app_commands.CommandTree):
    @tree.command(name="roymemory", description="Show a random roy moment from the past.")
    @app_commands.describe(num="Roy number to show")
    async def roymemory(interaction: discord.Interaction, num: int=0):
        if num < 0 or num > roy_count:
            await interaction.response.send_message(f"Invalid roy number. Current roy number is {roy_count}", ephemeral=True)
            return
        rnum = random.randint(142, roy_count) if num == 0 else num
        path = os.getcwd()
        msg_path = f"/message-imgs/roy-{rnum}"
        pic_path = f"/downloads/attachment-{rnum}"

        try:
            # Switched from jpeg to png at 492
            if rnum > 492:
                if os.path.exists(path + msg_path + ".png"):
                    await interaction.response.send_message(f"Roy #{rnum}", file=discord.File(path + msg_path + ".png"))
                else:
                    raise Exception("No message file")
            else:
                if os.path.exists(path + msg_path + ".jpeg"):
                    await interaction.response.send_message(f"Roy #{rnum}", file=discord.File(path + msg_path + ".jpeg"))
                else:
                    raise Exception("No message file")
            print(f"Sending roy #{rnum}")
        except Exception as e:
            print(e)
            print(f"No message image for roy #{rnum}, trying gif/image.")
            try:
                files = os.listdir(path + "/downloads")
                for file in files:
                    fname, ext = os.path.splitext(file)
                    if fname == f"attachment-{rnum}":
                        if ext == ".gif" and rnum < 1527:
                            continue
                        else:
                            await interaction.response.send_message(f"Roy #{rnum}", file=discord.File(f"{path}{pic_path}{ext}"))
                            print(f"Sending roy #{rnum}")
                            return
                print(f"No file found for roy {rnum}")
                await interaction.response.send_message(f"Roy #{rnum} is missing.", ephemeral=True)
            except Exception as e:
                print(f"Nothing found for roy #{rnum}.")
                print(e)

    print("roymemory added")