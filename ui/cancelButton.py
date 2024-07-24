import discord
from discord.ext import commands
from discord import app_commands
from services.overseerr import SearchResult, OverseerrManager


class CancelButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label=f"Cancel", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        try: 
            await interaction.message.delete()
            await interaction.response.send_message("Request cancelled.")
        except discord.errors.NotFound:
            await interaction.response.send_message("The original message has already been deleted.", ephemeral=True)