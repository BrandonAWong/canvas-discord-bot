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

API_URL = "https://csulb.instructure.com/"
API_KEY = os.getenv("API_KEY")

DISCORD_CLIENT = os.getenv("DISCORD_CLIENT")
client = commands.Bot(command_prefix="-", owner_id = 213366077852221441, intents=discord.Intents.all())

canvas = Canvas(API_URL, API_KEY)

# 1 - CECS 174 | 2 - CECS 174
IDS = {
    "COURSE_ID_1" : 31686,                    # change COURSE_ID per course
    "CHANNEL_ID_1" : 987096406214979634,      # snowflake | change according to where you want messages to default

    "COURSE_ID_2" : 3224,
    "CHANNEL_ID_2" : 1015747008641900624
    } 

def return_course_id(channel_name):
    if channel_name == "personal file":
        return IDS["COURSE_ID_1"]
    elif channel_name == "CECS 174 (FALL 2022)":
        return IDS["COURSE_ID_2"]

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
    if format == "include_hour":
        date_format = '%m/%d %I:%M %p'
    elif format == "only_hour":
        date_format = '%I:%M %p'
    else: 
        date_format = '%Y-%m-%d'
    date = utc.astimezone(timezone('US/Pacific'))
    return date.strftime(date_format)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await check_daily_reminder()

async def check_daily_reminder():
    while True: 
        if str(strftime("%H:%M")) == "16:30":
            daily_reminder.start('hello')
            break
        await asyncio.sleep(60)

@tasks.loop(hours = 24)
async def daily_reminder(ctx):
    for i in range (1, int(len(IDS)/2+1)):
        channel_id = IDS["CHANNEL_ID_"+str(i)]
        channel = client.get_channel(channel_id) 
        assignment_count_today = 0
        assignment_count_tomorrow = 0
        inner_value_today = ""
        inner_value_tomorrow = ""
        today = strftime("%A %m-%d")
        course = canvas.get_course(IDS["COURSE_ID_"+str(i)])
        assignments = course.get_assignments(
            bucket = 'upcoming', 
            order_by = 'due_at')
        embed = discord.Embed(
            title = f"⏰ {today}",
            color = 0xFFFF00)
        for assignment in assignments:
            due_date = utc_to_pst(assignment.due_at_date, "no_include_hour")
            due_hour = str(utc_to_pst(assignment.due_at_date, "only_hour"))
            if str(datetime.date.today()) == due_date:
                assignment_count_today += 1 
                inner_value_today += f"\n{assignment_count_today}. {str(assignment)}\n~  Due at {due_hour}\n"
            elif str(datetime.date.today() + datetime.timedelta(days=1)) == due_date:
                assignment_count_tomorrow += 1
                inner_value_tomorrow += f"\n{assignment_count_tomorrow}. {str(assignment)}\n~  Due at {due_hour}\n"
            else:
                break

        if assignment_count_today == 0:
            inner_value_today = "Nothing due today 🥳"
        if assignment_count_tomorrow == 0:
            inner_value_tomorrow = "Nothing due tomorrow 🎉"

        embed.add_field(name = "Assignments Due Today", value = inner_value_today, inline = False)
        embed.add_field(name = "Assignments Due Tomorrow", value = inner_value_tomorrow, inline = False)

        with open('facts.txt', 'r') as file:
            facts = file.read().splitlines()
            fact = random.choice(facts)

        embed.set_footer(text = f'Fact of the Day:\n{fact}')
        await channel.send(embed=embed)

@client.hybrid_command(name='commands', description='Listst sharko\'s commands')
async def commands(ctx):
    embed = discord.Embed(
        title ="🐧 Commands",
        color = 0x68BBE3)
    embed.add_field(name = "-due", value = "returns an assignment that should be priortized as it will be due soon", inline = False)
    embed.add_field(name = "-assignments", value = "returns a list of all upcoming assignments", inline = False)
    embed.add_field(name = "-source", value = "returns a link to source code", inline = False)
    embed.add_field(name = "-initialize", value = "intializes the server to recieve daily reminders", inline = False)
    embed.set_footer(text = 'Slash commands also work!')
    await ctx.message.channel.send(embed=embed)


@client.hybrid_command(name='due', description='Gives details about an upcoming assignment')
async def due(ctx):
    channel_name = ctx.message.guild.name
    try:
        assignment = return_assignments(channel_name)[0]
        title_url = return_url(channel_name)
        date = utc_to_pst(assignment.due_at_date, "include_hour")
        lock_date = utc_to_pst(assignment.lock_at_date, "include_hour")
        points = assignment.points_possible
        description = assignment.description
        bad_characters = ["<div>", "</div>", "<span>", "</span>", "<ul>", "</ul>", "<li>", "</li>", "<strong>", "</strong>", "<p>", "</p>", "&nbsp", ";"]
        for character in bad_characters:
            description = description.replace(character, "")
        embed = discord.Embed(
            title = f"📅 {str(assignment)}",
            url = title_url,
            color = 0xF4364C)
        embed.add_field(name = f"Due: {date}", value = f"Locks at: {lock_date}\n"
                                                    f"Points: {points}\n"
                                                    f"\n{description}")
    except:
        embed = discord.Embed(
            title = f"~ Nothing Due ~",
            color = 0xF4364C)
    await ctx.message.channel.send(embed=embed)

@client.hybrid_command(name='assignments', description='Lists out upcoming assignments')
async def assignments(ctx):
    channel_name = ctx.message.guild.name
    assignment_count = 0
    assignments = return_assignments(channel_name)
    title_url = return_url(channel_name)
    embed = discord.Embed(
        title ="📝 Assignments",
        url = title_url,
        color = 0x32CD30)
    for assignment in assignments:
        try:
            assignment_count += 1
            embed.add_field(name = f"{assignment_count}. {assignment}", value = f'Due: {utc_to_pst(assignment.due_at_date, "include_hour")}', inline = False)
        except:
            assignment_count -=1
    await ctx.message.channel.send(embed=embed)

@client.hybrid_command(name='source', description='Returns a link to sharko\'s source code')
async def source(ctx):
    embed = discord.Embed(
        title = "🐈‍⬛ Source Code",
        description = 'If you have a suggestion or come across a bug, make an issue / pull request or message me',
        url = "https://github.com/BrandonAWong/canvas",
        color = 0x333)
    embed.set_footer(icon_url = "https://cdn.discordapp.com/attachments/1016129238862135396/1083247345262673951/So_happy_smiling_cat-removebg-preview.png", text = "Brandon#4704")
    await ctx.message.channel.send(embed=embed)

@client.hybrid_command(name='initialize')
async def initialize(ctx):
    channel_name = ctx.message.guild.name
    if return_course_id(channel_name):
        await ctx.message.channel.send("Server Intialized ✅")
    else:
        await ctx.message.channel.send("Initialization Failed ❌\nMessage Brandon#4704")

@client.command()
#@commands.is_owner()
async def sync(ctx):
    try:
        await client.tree.sync()
        print('synced')
    except Exception as e:
        print(e)

client.run(DISCORD_CLIENT)
