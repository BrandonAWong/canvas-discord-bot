from time import strftime
from canvasapi import Canvas
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import datetime
import asyncio
import random
from util import *


DISCORD_CLIENT = os.getenv('DISCORD_CLIENT')
bot = commands.Bot(command_prefix='-', 
                      owner_id=213366077852221441, 
                      intents=discord.Intents.all())


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await load_cogs(bot)
    await check_daily_reminder()

async def load_cogs(bot):
    for file in os.listdir():
        if file.endswith('Cog.py'):
            await bot.load_extension(file[:-3])

async def check_daily_reminder():
    while True: 
        if str(strftime('%H:%M')) == '16:30':
            daily_reminder.start('hello')
            break
        await asyncio.sleep(60)

@tasks.loop(hours=24)
async def daily_reminder(ctx):
    with open('facts.txt', 'r') as file:
        facts = file.read().splitlines()
        fact = random.choice(facts)
    for i in range (1, int(len(IDS)/2+1)):
        channel_id = IDS['CHANNEL_ID_'+str(i)]
        channel = bot.get_channel(channel_id) 
        assignment_count_today = assignment_count_tomorrow = 0
        inner_value_today = inner_value_tomorrow = ''
        today = strftime('%A %m-%d')
        course = canvas.get_course(IDS['COURSE_ID_'+str(i)])
        assignments = course.get_assignments(
            bucket = 'upcoming', 
            order_by = 'due_at')
        embed = discord.Embed(
            title = f'⏰ {today}',
            color = 0xFFFF00)
        for assignment in assignments:
            due_date = utc_to_pst(assignment.due_at_date, 'no_include_hour')
            due_hour = str(utc_to_pst(assignment.due_at_date, 'only_hour'))
            if str(datetime.date.today()) == due_date:
                assignment_count_today += 1 
                inner_value_today += f'\n{assignment_count_today}. {str(assignment)}\n~  Due at {due_hour}\n'
            elif str(datetime.date.today() + datetime.timedelta(days=1)) == due_date:
                assignment_count_tomorrow += 1
                inner_value_tomorrow += f'\n{assignment_count_tomorrow}. {str(assignment)}\n~  Due at {due_hour}\n'
            else:
                break
        if assignment_count_today == 0:
            inner_value_today = 'Nothing due today 🥳'
        if assignment_count_tomorrow == 0:
            inner_value_tomorrow = 'Nothing due tomorrow 🎉'
        embed.add_field(name = 'Assignments Due Today', value = inner_value_today, inline = False)
        embed.add_field(name = 'Assignments Due Tomorrow', value = inner_value_tomorrow, inline = False)
        embed.set_footer(text = f'Fact of the Day:\n{fact}')
        await channel.send(embed=embed)

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