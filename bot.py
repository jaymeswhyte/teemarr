import discord
from discord import app_commands
import os
import requests
from services import qbit
from dotenv import load_dotenv, dotenv_values

load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
QBIT_USER = os.getenv("QBIT_USER")
QBIT_PASS = os.getenv("QBIT_PASS")
QBIT_ADDRESS= f"http://{os.getenv("QBIT_ADDRESS")}:{os.getenv("QBIT_PORT")}"

GUILD = discord.Object(id=GUILD_ID)
client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)

qbitManager=None


# COMMANDS
@tree.command( name="echo", description="Echo message", guild = GUILD)
async def echo(interaction: discord.Interaction, message:str):
    await interaction.response.send_message(message)

@tree.command(name="pause", description="Pause all torrents.", guild=GUILD)
async def pause(interaction: discord.Interaction):
    result = qbitManager.pause_all()
    if result:
        await interaction.response.send_message("Paused all active torrents.")
    else:
        await interaction.response.send_message("Failed to pause active torrents.")

@tree.command(name="resume", description="Resume all torrents.", guild=GUILD)
async def resume(interaction: discord.Interaction):
    result = qbitManager.resume_all()
    if result:
        await interaction.response.send_message("Resumed all inactive torrents.")
    else:
        await interaction.response.send_message("Failed to resume torrents.") 

# CLIENT EVENTS
@client.event
async def on_ready():
    global qbitManager
    await tree.sync(guild=GUILD)
    print("Connected to discord")
    qbitManager = qbit.QBitManager(QBIT_ADDRESS, QBIT_USER, QBIT_PASS)

session = requests.Session()
client.run(TOKEN)