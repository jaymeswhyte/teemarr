import discord
from discord.ext import commands
from discord import app_commands
from services.overseerr import SearchResult


class RequestButton(discord.ui.Button):
    def __init__(self, item: SearchResult):
        if item._year != "": yearStr = f"({item._year})"
        else: yearStr = ""
        super().__init__(label=f"{item._title} {yearStr}", style=discord.ButtonStyle.primary)
        self.item = item

    async def callback(self, interaction: discord.Interaction):
        await handle_request(interaction, self.item)

async def handle_request(interaction: discord.Interaction, item: SearchResult):
    # Define what happens when the button is pressed
    await interaction.response.send_message(f"Requested: {item._title} ({item._year})")