import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, time
import os
from services import qbit, overseerr, webhookserver, dbmanager
from ui import requestButton, cancelButton, requestView
from components.config import Config
from components.torrentListing import TorrentListing
from utils.TeemoUtilities import *
from dotenv import load_dotenv
import pytz
import logging
import asyncio

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

WEBHOOK_PORT = os.environ["WEBHOOK_PORT"]

STATUS_CHANNEL_NAME = os.environ["STATUS_CHANNEL"]
NOTIFICATION_CHANNEL_NAME = os.environ["NOTIFICATION_CHANNEL"]

TZ_NAME = os.environ['TZ']
if not TZ_NAME:
    TZ_NAME = 'UTC'
timezone = pytz.timezone(TZ_NAME)
local_tz = datetime.now().astimezone().tzinfo
nightTime = time(hour=1, minute=0, tzinfo=local_tz)
dayTime = time(hour=9, minute=0, tzinfo=local_tz)

client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)

qbitManager = None
overseerrManager = None
webhookServer = webhookserver.WebhookServer(WEBHOOK_PORT)

guild = None
statusChannel = None
notificationChannel = None
configuration = None

configPath = None
if os.path.exists('/config'): configPath = '/config'
else: configPath = 'config'

databasePath = os.path.join(configPath, 'database')
os.makedirs(databasePath, exist_ok=True) # Create subdirectory if it doesn't exist

dbManager = dbmanager.DBManager(databasePath)

# COMMANDS
@tree.command( name="echo", description="Echo message", guild = GUILD_OBJECT)
async def echo(interaction: discord.Interaction, message:str):
    await interaction.response.send_message(message)

@tree.command(name="pause", description="Pause all torrents.", guild = GUILD_OBJECT)
async def pause(interaction: discord.Interaction):
    global qbitManager
    result = qbitManager.pause_all()
    if result:
        await interaction.response.send_message(":octagonal_sign: Paused all active torrents.")
    else:
        await interaction.response.send_message(":x: Failed to pause active torrents.")

@tree.command(name="resume", description="Resume all torrents.", guild=GUILD_OBJECT)
async def resume(interaction: discord.Interaction):
    global qbitManager
    result = qbitManager.resume_all()
    if result:
        await interaction.response.send_message(":white_check_mark: Resumed all paused torrents.")
    else:
        await interaction.response.send_message(":x: Failed to resume torrents.") 

@tree.command(name="torrentlist", description="List active torrents.", guild=GUILD_OBJECT)
async def torrentlist(interaction: discord.Interaction):
    global qbitManager
    torrentList = qbitManager.info()
    if len(torrentList)>0:
        embed = discord.Embed(title=f"Active Torrents", color=discord.Color.dark_grey())
        for torrentListing in torrentList:
            torrentInfo = f""
            stalled = False
            paused = False
            if torrentListing.state == "downloading": 
                if torrentListing.seeds == 0: 
                    torrentInfo+=":infinity: "
                    stalled = True
                else: torrentInfo+=":arrow_double_down: "
            elif torrentListing.state == "paused": 
                paused = True
                torrentInfo+=":pause_button: "
            torrentInfo+=f"{int(100*torrentListing.progress)}%"
            roundedPercent = int(10*round(torrentListing.progress, 1))
            torrentInfo+=":blue_square:"*roundedPercent
            torrentInfo+=":white_large_square:"*(10-roundedPercent)
            if stalled: stalledStr = " (Stalled)"
            else: stalledStr = ""
            if paused: pausedStr = " (Paused)"
            else: pausedStr = ""
            torrentInfo+=f" {torrentListing.seeds} Seeds{stalledStr}{pausedStr}."
            embed.add_field(name=torrentListing.title, value=torrentInfo, inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("There are no torrents currently downloading.")

@tree.command(name="request", description="Request a Title.", guild=GUILD_OBJECT)
async def request(interaction: discord.Interaction, query:str):
    global overseerrManager, dbManager
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
                description = searchResult._description
                embed = discord.Embed(
                    title=f"{searchResult._title} {yearStr}",
                    description=f"{searchResult._type}\n-# {description}",
                    color=discord.Color.dark_grey()
                )
                embeds.append(embed)
                view.add_item(requestButton.RequestButton(searchResult, overseerrManager, dbManager))
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
    global qbitManager, overseerrManager, statusChannel, notificationChannel, configuration, guild, webhookServer
    guild = await client.fetch_guild(GUILD_ID)
    await tree.sync(guild=guild)
    channels = await guild.fetch_channels()
    print("Connected to discord")
    qbitManager = qbit.QBitManager(QBIT_ADDRESS, QBIT_USER, QBIT_PASS)
    overseerrManager = overseerr.OverseerrManager(OVERSEERR_ADDRESS, OVERSEERR_KEY)
    statusChannel = discord.utils.get(channels, name=STATUS_CHANNEL_NAME)
    notificationChannel = discord.utils.get(channels, name=NOTIFICATION_CHANNEL_NAME)
    if not statusChannel: statusChannel = guild.channels[0]
    embeds = []
    with open('version.txt', 'r') as file:
        version = file.readline().strip()
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
    check_webhooks.start()

@tasks.loop(minutes=5)
async def check_webhooks():
    global webhookServer, dbManager
    while not webhookServer.queue.empty():
        try:
            payload = await webhookServer.queue.get()
            event = payload['event']
            if event == "library.on.deck" or event=="library.new":
                serverName = payload['Server']['title']
                metadata = payload['Metadata']
                mediaType = metadata['type']
                tmdbID = None
                requesterID = None
                pingString = ""
                for guid in metadata["Guid"]:
                    if guid["id"].startswith("tmdb://"):
                        tmdbID = int(guid["id"].split("tmdb://")[1])
                        break
                descriptionStr = f"-# {metadata['summary']}"
                titleStr = f"{metadata['title']}"
                if tmdbID != None:
                    requestRecord = dbManager.getRequest(tmdbID)
                    if requestRecord != None: 
                        requesterID = requestRecord['user']
                        pingString = f"<@{requesterID}>"
                    showStr = ""
                    if mediaType == "episode": 
                        showStr = f"**{metadata['grandparentTitle']}** "
                        titleStr = f"{metadata['parentTitle']} Episode {metadata['index']} - {metadata['title']}"
                        descriptionStr = f"-# ||{metadata['summary']}||"
                embed = discord.Embed(
                        title=titleStr,
                        description=descriptionStr,
                        color=discord.Color.dark_grey()
                    )
                await notificationChannel.send(f"New {showStr}{mediaType} on {serverName}! {pingString}", embeds=[embed])
        except Exception as e:
            logging.error(f"Exception encountered whilst handling webhook: {e}")
            

@tasks.loop(time=nightTime)
async def overnight_resume():
    global configuration, qbitManager
    if configuration.overnightDownloads:
        result = qbitManager.resume_all()
        if result:
            await statusChannel.send(f"Goodnight! Downloads are being resumed for the night. Sleep well!")
        else:
            await statusChannel.send(f"Goodnight! I couldn't resume downloads for the night.")

@tasks.loop(time=dayTime)
async def daytime_pause():
    global configuration, qbitManager
    if configuration.overnightDownloads:
        result = qbitManager.pause_all()
        if result:
            await statusChannel.send(f"Good Morning! Downloads have been paused.")
        else:
            await statusChannel.send(f"Good Morning! I couldn't pause downloads for the day.")

async def main():
    # Start the webhook server in the background
    asyncio.create_task(webhookServer.start())

    # Start the Discord bot (it will block the execution)
    await client.start(TOKEN)

asyncio.run(main())  # Keep this here, as `main()` properly manages the event loop now.
