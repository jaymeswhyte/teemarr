import discord
from discord.ext import commands
from discord import app_commands
from services.overseerr import SearchResult, OverseerrManager
from services.dbmanager import DBManager
from datetime import datetime


class RequestButton(discord.ui.Button):
    def __init__(self, item: SearchResult, manager:OverseerrManager, databaseManager:DBManager):
        self.manager = manager
        self.dbManager = databaseManager
        if item._year != "": yearStr = f"({item._year})"
        else: yearStr = ""
        if len(item._title) >= 74: item._title = item._title[0:70]+"..."
        super().__init__(label=f"{item._title} {yearStr}", style=discord.ButtonStyle.primary)
        self.item = item

    async def callback(self, interaction: discord.Interaction):
        await handle_request(interaction, self.item, self.manager, self.dbManager)

async def handle_request(interaction: discord.Interaction, item: SearchResult, manager: OverseerrManager, dbmanager:DBManager):
    requestResult = manager.request(item)
    if item._year != "": yearStr = f" ({item._year})"
    else: yearStr = ""
    if requestResult:
        titleData = item.rawData
        dbmanager.insertRequest(titleData['id'], interaction.user.id, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        await interaction.message.delete()
        await interaction.response.send_message(f"Requested: {item._title}{yearStr}.")
    else:
        await interaction.response.send_message(f"Failed to request {item._title}{yearStr}.")