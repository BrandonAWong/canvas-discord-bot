import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_CLIENT = os.getenv('DISCORD_CLIENT')
bot = commands.Bot(command_prefix='-', 
                      owner_id=213366077852221441, 
                      intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await load_cogs(bot)

async def load_cogs(bot):
    for file in os.listdir('./Cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f'Cogs.{file[:-3]}')

@bot.command()
@commands.is_owner() 
async def sync(ctx):
    await bot.tree.sync()
    await ctx.reply('synced')

@bot.command()
@commands.is_owner() 
async def clearTree(ctx):
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()
    await ctx.reply('cleared and synced')

bot.run(DISCORD_CLIENT)