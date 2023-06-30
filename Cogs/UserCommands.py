import discord
from discord.ext import commands
from util import *


class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='commands-list', description='Lists sharko\'s commands',)
    async def commands_list(self, ctx: commands.Context) -> None:
        embed = discord.Embed(
            title = '🐧 Help',
            color = 0x68BBE3)
        embed.add_field(name = '-due', value = 'returns an assignment that will be due soon', inline = False)
        embed.add_field(name = '-assignments', value = 'returns a list of all upcoming assignments', inline = False)
        embed.add_field(name = '-source', value = 'returns a link to source code', inline = False)
        embed.set_footer(text = 'Slash commands also work!')
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name='due', description='Gives details about an upcoming assignment')
    async def due(self, ctx: commands.Context):
        channel_name = ctx.message.guild.name
        try:
            assignment = return_assignments(channel_name)[0]
            title_url = return_url(channel_name)
            date = utc_to_pst(assignment.due_at_date, 'include_hour')
            points = assignment.points_possible
            description = assignment.description[0:1023]
            bad_characters = ['<div>', '</div>', '<span>', '</span>', '<ul>', 
                            '</ul>', '<li>', '</li>', '<strong>', '</strong>', 
                            '<p>', '</p>', '<em>', '</em>', '&nbsp', ';']
            for character in bad_characters:
                description = description.replace(character, '')
            embed = discord.Embed(
                title = f'📅 {str(assignment)}',
                url = title_url,
                color = 0xF4364C)
            embed.add_field(name = f'Due: {date}', 
                            value = f'Points: {points}\n\n{description}')
        except:
            embed = discord.Embed(
                title = f'~ Nothing Due ~',
                color = 0xF4364C)
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name='assignments', description='Lists out upcoming assignments')
    async def assignments(self, ctx: commands.Context) -> None:
        channel_name = ctx.message.guild.name
        assignment_count = 0
        assignments = return_assignments(channel_name)
        title_url = return_url(channel_name)
        embed = discord.Embed(
            title ='📝 Assignments',
            url = title_url,
            color = 0x32CD30)
        for assignment in assignments:
            try:
                assignment_count += 1
                embed.add_field(name = f'{assignment_count}. {assignment}', 
                                value = f'Due: {utc_to_pst(assignment.due_at_date, "include_hour")}', 
                                inline = False)
            except:
                assignment_count -=1
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name='source', description='Returns a link to sharko\'s source code')
    async def source(self, ctx: commands.Context) -> None:
        embed = discord.Embed(
            title = '🐈‍⬛ Source Code',
            url = 'https://github.com/BrandonAWong/canvas-discord-bot',
            color = 0x333)
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UserCommands(bot))