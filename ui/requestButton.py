import discord
from discord.ext import commands
from discord import app_commands
from services.overseerr import SearchResult, OverseerrManager


class RequestButton(discord.ui.Button):
    def __init__(self, item: SearchResult, manager:OverseerrManager):
        self.manager = manager
        if item._year != "": yearStr = f"({item._year})"
        else: yearStr = ""
        super().__init__(label=f"{item._title} {yearStr}", style=discord.ButtonStyle.primary)
        self.item = item

    async def callback(self, interaction: discord.Interaction):
        await handle_request(interaction, self.item, self.manager)

async def handle_request(interaction: discord.Interaction, item: SearchResult, manager: OverseerrManager):
    requestResult = manager.request(item)
    if item._year != "": yearStr = f" ({item._year})"
    else: yearStr = ""
    if requestResult:
        await interaction.response.send_message(f"Requested: {item._title}{yearStr}.")
    else:
        await interaction.response.send_message(f"Failed to request {item._title}{yearStr}.")