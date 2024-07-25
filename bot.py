import discord
from discord import app_commands
import os
import requests
from services import qbit, overseerr
from ui import requestButton, cancelButton
from components.config import Config
from utils.TeemoUtilities import *
from dotenv import load_dotenv, dotenv_values

load_dotenv()
TOKEN = os.environ["TOKEN"]
GUILD_ID = int(os.environ["GUILD_ID"])

QBIT_USER = os.environ["QBIT_USER"]
QBIT_PASS = os.environ["QBIT_PASS"]
QBIT_ADDRESS= f"http://{os.environ['QBIT_ADDRESS']}:{os.environ['QBIT_PORT']}"

OVERSEERR_KEY = os.environ["OVERSEERR_KEY"]
OVERSEERR_ADDRESS = f"http://{os.environ['OVERSEERR_ADDRESS']}:{os.environ['OVERSEERR_PORT']}"

GUILD = discord.Object(id=GUILD_ID)
client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)

qbitManager=None
overseerrManager = None

statusChannel = None
configuration = None

configPath = None
if os.path.exists('/config'): configPath = '/config'
else: configPath = 'config'

# COMMANDS
@tree.command( name="echo", description="Echo message", guild = GUILD)
async def echo(interaction: discord.Interaction, message:str):
    await interaction.response.send_message(message)

@tree.command(name="pause", description="Pause all torrents.", guild=GUILD)
async def pause(interaction: discord.Interaction):
    result = qbitManager.pause_all()
    if result:
        await interaction.response.send_message(":octagonal_sign: Paused all active torrents.")
    else:
        await interaction.response.send_message(":x: Failed to pause active torrents.")

@tree.command(name="resume", description="Resume all torrents.", guild=GUILD)
async def resume(interaction: discord.Interaction):
    result = qbitManager.resume_all()
    if result:
        await interaction.response.send_message(":white_check_mark: Resumed all paused torrents.")
    else:
        await interaction.response.send_message(":x: Failed to resume torrents.") 

@tree.command(name="request", description="Request a Title.", guild=GUILD)
async def request(interaction: discord.Interaction, query:str):
    searchResults = overseerrManager.search(query)
    view = discord.ui.View()
    embeds = []
    if len(searchResults)>0:
        count = 0
        for searchResult in searchResults:
            count+=1
            if count <= 9:
                if searchResult._year != "": yearStr = f"({searchResult._year})"
                else: yearStr = ""
                embed = discord.Embed(
                    title=f"{searchResult._title} {yearStr}",
                    description=f"{searchResult._type}\n-# {searchResult._description}",
                    color=discord.Color.dark_grey()
                )
                embeds.append(embed)
                view.add_item(requestButton.RequestButton(searchResult, overseerrManager))
        view.add_item(cancelButton.CancelButton())
        await interaction.response.send_message(embeds=embeds, view=view)
    else:
        await interaction.response.send_message("No titles found.")

# CLIENT EVENTS
@client.event
async def on_ready():
    global qbitManager, overseerrManager, statusChannel, configuration
    await tree.sync(guild=GUILD)
    print("Connected to discord")
    qbitManager = qbit.QBitManager(QBIT_ADDRESS, QBIT_USER, QBIT_PASS)
    overseerrManager = overseerr.OverseerrManager(OVERSEERR_ADDRESS, OVERSEERR_KEY)
    statusChannel = discord.utils.get(GUILD.channels, name="status")
    embeds = []
    with open('version.txt', 'r') as file:
        version = file.readline()
        file.close()
    configuration = Config(configPath)
    if configuration.is_older_than(version):
        configuration.version = version
        configuration.write_to_file(configPath)
        notes = get_release_notes(configuration.version)
        embed = discord.Embed(
                    title=f"New release patch notes: v{configuration.version}",
                    description=notes,
                    color=discord.Color.dark_grey()
                )
        embeds.append(embed)
    await statusChannel.send(f"Back Online! Running Teemarr v{configuration.version}.", embeds=embeds)

session = requests.Session()
client.run(TOKEN)