import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, time
import os
from services import qbit, overseerr
from ui import requestButton, cancelButton, requestView
from components.config import Config
from utils.TeemoUtilities import *
from dotenv import load_dotenv
import pytz

# Environment variables
load_dotenv()
TOKEN = os.environ["TOKEN"]
GUILD_ID = int(os.environ["GUILD_ID"])
GUILD_OBJECT = discord.Object(id=GUILD_ID)

QBIT_USER = os.environ["QBIT_USER"]
QBIT_PASS = os.environ["QBIT_PASS"]
QBIT_ADDRESS= f"http://{os.environ['QBIT_ADDRESS']}:{os.environ['QBIT_PORT']}"

OVERSEERR_KEY = os.environ["OVERSEERR_KEY"]
OVERSEERR_ADDRESS = f"http://{os.environ['OVERSEERR_ADDRESS']}:{os.environ['OVERSEERR_PORT']}"

TZ_NAME = os.environ['TZ']
if not TZ_NAME:
    TZ_NAME = 'UTC'
timezone = pytz.timezone(TZ_NAME)
local_tz = datetime.now().astimezone().tzinfo
nightTime = time(hour=1, minute=0, tzinfo=local_tz)
dayTime = time(hour=9, minute=0, tzinfo=local_tz)

client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)

qbitManager=None
overseerrManager = None

guild = None
statusChannel = None
configuration = None


configPath = None
if os.path.exists('/config'): configPath = '/config'
else: configPath = 'config'

# COMMANDS
@tree.command( name="echo", description="Echo message", guild = GUILD_OBJECT)
async def echo(interaction: discord.Interaction, message:str):
    await interaction.response.send_message(message)

@tree.command(name="pause", description="Pause all torrents.", guild = GUILD_OBJECT)
async def pause(interaction: discord.Interaction):
    result = qbitManager.pause_all()
    if result:
        await interaction.response.send_message(":octagonal_sign: Paused all active torrents.")
    else:
        await interaction.response.send_message(":x: Failed to pause active torrents.")

@tree.command(name="resume", description="Resume all torrents.", guild=GUILD_OBJECT)
async def resume(interaction: discord.Interaction):
    result = qbitManager.resume_all()
    if result:
        await interaction.response.send_message(":white_check_mark: Resumed all paused torrents.")
    else:
        await interaction.response.send_message(":x: Failed to resume torrents.") 

@tree.command(name="request", description="Request a Title.", guild=GUILD_OBJECT)
async def request(interaction: discord.Interaction, query:str):
    searchResults = overseerrManager.search(query)
    view = requestView.RequestView(timeout=60)
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
        view.message = await interaction.original_response()
    else:
        await interaction.response.send_message("No titles found.")

@tree.command(name="overnights", description="Turn overnight values ON or OFF", guild=GUILD_OBJECT)
async def overnights(interaction: discord.Interaction, setting:str):
    global configuration
    oldSetting = configuration.overnightDownloads
    setting = setting.upper() # Formatting
    if setting == "ON" or setting == "TRUE":
        configuration.overnightDownloads = True
        await interaction.response.send_message("Overnight Downloads are now ON.")
    elif setting == "OFF" or setting == "FALSE":
        configuration.overnightDownloads = False
        await interaction.response.send_message("Overnight Downloads are now OFF.")

    if configuration.overnightDownloads != oldSetting: 
        configuration.write_to_file(configPath) # Only bother with write operation if this value is different



# CLIENT EVENTS
@client.event
async def on_ready():
    global qbitManager, overseerrManager, statusChannel, configuration, guild
    guild = await client.fetch_guild(GUILD_ID)
    await tree.sync(guild=guild)
    channels = await guild.fetch_channels()
    print("Connected to discord")
    qbitManager = qbit.QBitManager(QBIT_ADDRESS, QBIT_USER, QBIT_PASS)
    overseerrManager = overseerr.OverseerrManager(OVERSEERR_ADDRESS, OVERSEERR_KEY)
    statusChannel = discord.utils.get(channels, name="status")
    if not statusChannel: statusChannel = guild.channels[0]
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
    print(f"TZ: {timezone}\tTime:{datetime.now(timezone)}\tNight:{nightTime}")
    overnight_resume.start()
    daytime_pause.start()


@tasks.loop(time=nightTime)
async def overnight_resume():
    global configuration
    if configuration.overnightDownloads:
        result = qbitManager.resume_all()
        if result:
            await statusChannel.send(f"Goodnight! Downloads are being resumed for the night. Sleep well!")
        else:
            await statusChannel.send(f"Goodnight! I couldn't resume downloads for the night.")

@tasks.loop(time=dayTime)
async def daytime_pause():
    global configuration
    if configuration.overnightDownloads:
        result = qbitManager.pause_all()
        if result:
            await statusChannel.send(f"Good Morning! Downloads have been paused.")
        else:
            await statusChannel.send(f"Good Morning! I couldn't pause downloads for the day.")

client.run(TOKEN)