import discord
from discord import app_commands
from discord.ext import commands
from util import *


class Admin(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.help_link = 'https://docs.google.com/document/d/17O27VwJ_KlOzfie85Enp58lcKrB0LOo0rgvrY4XqJCE/edit'

    @app_commands.command(name='help', description='Gives a list of admin commands')
    @app_commands.checks.has_permissions(administrator=True)
    async def help(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title = '🔌 Admin Commands',
            color = 0xFFBF00)
        embed.add_field(name = '/help-initialize', 
                        value = 'Returns a link to help with setting up the bot', 
                        inline = False)
        embed.add_field(name = '/initialize', 
                        value = 'Sets up the server to recieve daily reminders', 
                        inline = False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='help-initialize', description='Gives Instructions for setting up the bot')
    @app_commands.checks.has_permissions(administrator=True)
    async def help_initialize(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title = '🌌 Setup Help',
            url = self.help_link,
            color = 0xBF40BF)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='initialize', description='First time setup for bot')
    @app_commands.checks.has_permissions(administrator=True)
    async def initialize(self, interaction: discord.Interaction, org: str, course_id: str, token: str) -> None:
        status = upload_row(interaction.guild_id, interaction.channel_id, org, int(course_id), token)
        if status:
            embed = discord.Embed(
                title = 'Server Intialized ✔',
                color = 0x00FF00)
        else:
            embed = discord.Embed(
                title = 'Initialization Failed ❌',
                url = self.help_link,
                description = 'Click on the link for help',
                color = 0xFF5733 )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))