import discord
from discord.ext import commands
from dotenv import load_dotenv
import os


load_dotenv()
DISCORD_CLIENT = os.getenv('DISCORD_CLIENT')
bot = commands.Bot(
    command_prefix='-',  
    intents=discord.Intents.all())
bot.remove_command('help')

@bot.event
async def on_ready() -> None:
    await load_cogs(bot)
    print(f'We have logged in as {bot.user}')
    
async def load_cogs(bot: commands.Bot) -> None:
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f'cogs.{file[:-3]}')

bot.run(DISCORD_CLIENT)