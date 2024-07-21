import discord
from discord import app_commands
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)

@tree.command(
        name="echo",
        description="Echo input",
        guild = discord.Object(id=GUILD_ID)

)
async def echo(interaction: discord.Interaction, message:str):
    await interaction.response.send_message(message)

# CLIENT EVENTS
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print("Connected")


client.run(TOKEN)