import discord
from discord import app_commands
from discord.ext import commands
from util import return_course_id


class Admin(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='commands', description='Gives list of admin commands')
    @app_commands.checks.has_permissions(administrator=True)
    async def commands(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title = '🔌 Admin Commands',
            color = 0x68BBE3)
        embed.add_field(name = '/help-initialize', value = 'Returns a link to help with setting up the server', inline = False)
        embed.add_field(name = '/initialize', value = 'Sets up the server to recieve daily reminders', inline = False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='help-initialize', description='Gives Instructions for setting up the bot')
    @app_commands.checks.has_permissions(administrator=True)
    async def help_initialize(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title = '🌌 Setup Help',
            url = 'https://docs.google.com/document/d/17O27VwJ_KlOzfie85Enp58lcKrB0LOo0rgvrY4XqJCE/edit',
            color = 0x68BBE3)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='initialize', description='First time setup for bot')
    @app_commands.checks.has_permissions(administrator=True)
    async def initialize(self, interaction: discord.Interaction, org: str, course_id: str, token: str) -> None:
        channel_id = interaction.guild.id
        channel_name = interaction.guild.name
        if return_course_id(channel_name):
            embed = discord.Embed(
                title = 'Server Intialized ✔',
                color = 0x00FF00)
            await interaction.response.send_message(embed=embed)
            print(f'{org} {course_id} {token}')
        else:
            embed = discord.Embed(
                title = 'Initialization Failed ❌',
                url = 'https://docs.google.com/document/d/17O27VwJ_KlOzfie85Enp58lcKrB0LOo0rgvrY4XqJCE/edit?usp=sharing',
                description = 'Click on the link for help',
                color = 0xFF5733 )
            await interaction.response.send_message(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Admin(bot))