from time import strftime
from canvasapi import Canvas
from pytz import timezone
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import datetime
import asyncio
import random
# todo - organize code (cogs, util.py), slash commands, database for multitude of classes, change how the daily remidner is sent


load_dotenv()

API_URL = 'https://csulb.instructure.com/'
API_KEY = os.getenv('API_KEY')

DISCORD_CLIENT = os.getenv('DISCORD_CLIENT')
client = commands.Bot(command_prefix='-', owner_id = 213366077852221441, intents=discord.Intents.all())

canvas = Canvas(API_URL, API_KEY)

# 1 - CECS 174 | 2 - CECS 174
IDS = {
    'COURSE_ID_1' : 31686,                    # change COURSE_ID per course
    'CHANNEL_ID_1' : 987096406214979634,      # snowflake | change according to where you want messages to default

    'COURSE_ID_2' : 3224,
    'CHANNEL_ID_2' : 1015747008641900624
    } 

def return_course_id(channel_name):
    if channel_name == 'personal file':
        return IDS['COURSE_ID_1']
    elif channel_name == 'CECS 174 (FALL 2022)':
        return IDS['COURSE_ID_2']

def return_course(channel_name):
    id = return_course_id(channel_name)
    return canvas.get_course(id)

def return_assignments(channel_name):
    course = return_course(channel_name)
    assignments = course.get_assignments(
        bucket = 'future', 
        order_by = 'due_at')
    return assignments

def return_url(channel_name):
    id = return_course_id(channel_name)
    return f'{API_URL}courses/{id}/assignments'

def utc_to_pst(utc, format):
    if format == 'include_hour':
        date_format = '%m/%d %I:%M %p'
    elif format == 'only_hour':
        date_format = '%I:%M %p'
    else: 
        date_format = '%Y-%m-%d'
    date = utc.astimezone(timezone('US/Pacific'))
    return date.strftime(date_format)

@client.command()
@commands.is_owner() 
async def sync(ctx):
    try:
        await client.tree.sync()
        await ctx.reply('synced')
        print('synced')
    except Exception as e:
        await ctx.reply(e)
        print(e)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await check_daily_reminder()

async def check_daily_reminder():
    while True: 
        if str(strftime('%H:%M')) == '16:30':
            daily_reminder.start('hello')
            break
        await asyncio.sleep(60)

@tasks.loop(hours = 24)
async def daily_reminder(ctx):
    with open('facts.txt', 'r') as file:
        facts = file.read().splitlines()
        fact = random.choice(facts)
    for i in range (1, int(len(IDS)/2+1)):
        channel_id = IDS['CHANNEL_ID_'+str(i)]
        channel = client.get_channel(channel_id) 
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

@client.hybrid_command(name='commands', description='Lists sharko\'s commands')
async def commands(ctx):
    embed = discord.Embed(
        title ='🐧 Commands',
        color = 0x68BBE3)
    embed.add_field(name = '-due', value = 'returns an assignment that should be priortized as it will be due soon', inline = False)
    embed.add_field(name = '-assignments', value = 'returns a list of all upcoming assignments', inline = False)
    embed.add_field(name = '-source', value = 'returns a link to source code', inline = False)
    embed.add_field(name = '/initialize', value = 'ONLY FOR SERVER OWNER: sets up the server to recieve daily reminders', inline = False)
    embed.set_footer(text = 'Slash commands also work!')
    await ctx.reply(embed=embed)

@client.hybrid_command(name='due', description='Gives details about an upcoming assignment')
async def due(ctx):
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
        embed.add_field(name = f'Due: {date}', value = f'Points: {points}\n'
                                                       f'\n{description}')
    except:
        embed = discord.Embed(
            title = f'~ Nothing Due ~',
            color = 0xF4364C)
    await ctx.reply(embed=embed)

@client.hybrid_command(name='assignments', description='Lists out upcoming assignments')
async def assignments(ctx):
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

@client.hybrid_command(name='source', description='Returns a link to sharko\'s source code')
async def source(ctx):
    embed = discord.Embed(
        title = '🐈‍⬛ Source Code',
        url = 'https://github.com/BrandonAWong/canvas',
        color = 0x333)
    await ctx.reply(embed=embed)

@client.tree.command(name='initialize', description='First time setup for bot')
async def initialize(ctx, org: str, course_id: str, token: str, guild_id: str):
    if ctx.user.id == ctx.guild.owner_id:  
        #channel_name = ctx.guild.id
        channel_name = ctx.guild.name
        if return_course_id(channel_name):
            await ctx.response.send_message('Server Intialized ✅')
            print(f'{org} {course_id} {token} {guild_id}')
        else:
            await ctx.response.send_message('Initialization Failed ❌')
    else:
        await ctx.response.send_message('Only for server admins!')

client.run(DISCORD_CLIENT)

#dictionary (key = channel id so its a list of channel ids) --> dictionary (that dictionary then holds info of that channel like url and such)

# need (secret token, org, course id, channel for reminders)