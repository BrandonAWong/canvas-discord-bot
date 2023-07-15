import discord
from discord.ext import commands
from util import *


class UserCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name='help', description='Gives a list of commands')
    async def help(self, ctx: commands.Context) -> None:
        embed = discord.Embed(
            title = '🐧 Help',
            color = 0x68BBE3)

        embed.add_field(
            name = '-due', 
            value = 'returns an assignment that will be due soon', 
            inline = False)
        
        embed.add_field(
            name = '-assignments', 
            value = 'returns a list of upcoming assignments', 
            inline = False)
        
        embed.add_field(
            name = '-source', 
            value = 'returns a link to source code', 
            inline = False)
        
        embed.set_footer(text = 'Slash commands also work!')
        
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name='due', description='Gives details about an upcoming assignment')
    async def due(self, ctx: commands.Context):
        await ctx.defer()
        server_id: int = ctx.message.guild.id
        assignments: list = return_assignments(server_id)

        if len(list(assignments)) > 0:
            assignment = assignments[0]
            description: str = assignment.description[:1023]
            bad_characters: tuple = ('<div>', '</div>', '<span>', '</span>', '<ul>', 
                            '</ul>', '<li>', '</li>', '<strong>', '</strong>', 
                            '<p>', '</p>', '<em>', '</em>', '&nbsp', ';')
            
            for character in bad_characters:
                description = description.replace(character, '')

            due_date: str = convert_tz(
                server_id, due_date, 
                assignment.due_at_date, 
                "%m/%d %I:%M %p")
            
            embed = discord.Embed(
                title = f'📅 {assignment.name}',
                url = return_assignments_url(server_id),
                color = 0xF4364C)
            
            embed.add_field(
                name = f'Due: {due_date}',
                value = f'Points: {assignment.points_possible}\n'
                        f'\n{description}')
        else:
            embed = discord.Embed(
                title = '~ Nothing Due ~',
                color = 0xF4364C)
            
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name='assignments', description='Lists out upcoming assignments')
    async def assignments(self, ctx: commands.Context) -> None:
        await ctx.defer()
        server_id: int = ctx.message.guild.id
        assignments: list = return_assignments(server_id)

        embed = discord.Embed(
            title = '📝 Assignments',
            url = return_assignments_url(server_id),
            color = 0x32CD30)
        
        for i, assignment in enumerate(assignments):
            due_date: str = convert_tz(
                server_id, due_date, 
                assignment.due_at_date, 
                "%m/%d %I:%M %p")
            embed.add_field(
                name = f'{i+1}. {assignment.name}', 
                value = f'Due: {due_date}',
                inline = False)
            
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name='source', description='Returns a link to source code')
    async def source(self, ctx: commands.Context) -> None:
        embed = discord.Embed(
            title = '🐈‍⬛ Source Code',
            url = 'https://github.com/BrandonAWong/canvas-discord-bot',
            color = 0x333)
        
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UserCommands(bot))