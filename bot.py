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

qbitManager:qbit.QBitManager


# COMMANDS
@tree.command( name="echo", description="Echo message", guild = GUILD)
async def echo(interaction: discord.Interaction, message:str):
    await interaction.response.send_message(message)

# CLIENT EVENTS
@client.event
async def on_ready():
    await tree.sync(guild=GUILD)
    print("Connected to discord")
    qbitManager = qbit.QBitManager(QBIT_ADDRESS, QBIT_USER, QBIT_PASS)

session = requests.Session()
client.run(TOKEN)