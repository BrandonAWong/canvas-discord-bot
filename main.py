from time import strftime
from canvasapi import Canvas
from pytz import timezone
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import datetime
import asyncio

load_dotenv()

API_URL = "https://csulb.instructure.com/"
API_KEY = os.getenv("API_KEY")

DISCORD_CLIENT = os.getenv("DISCORD_CLIENT")
client = commands.Bot(command_prefix="-", intents=discord.Intents.all())

canvas = Canvas(API_URL, API_KEY)

# 1 - CECS 174 | 2 - 
IDS = {
    "COURSE_ID_1" : 3224,                   # change COURSE_ID per course
    "CHANNEL_ID_1" : 1011740189682581618    # snowflake | change according to where you want messages to default
    } 

def return_course_id(channel_name):
    if channel_name == "CECS 174":
        return IDS["COURSE_ID_1"]

def return_course(channel_name):
    id = return_course_id(channel_name)
    return canvas.get_course(id)

# get assignment list | returns paginated list 
def return_assignments(channel_name):
    course = return_course(channel_name)
    assignments = course.get_assignments(
        bucket = 'upcoming', 
        order_by = 'due_at')
    return assignments

def return_url(channel_name):
    id = return_course_id(channel_name)
    return f'{API_URL}courses/{id}/assignments'

# convert utc to pst
def utc_to_pst(utc, format):
    if format == "include_hour":
        date_format = '%m/%d %H:%M'
    else: 
        date_format = '%Y-%m-%d'
    date = utc.astimezone(timezone('US/Pacific'))
    return date.strftime(date_format)

# on start | debug & daily_reminder start loop
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await check_daily_reminder()

async def check_daily_reminder():
    while True: 
        if str(strftime("%H:%M")) == "15:30":
            daily_reminder.start("DONT REMOVE THIS PARAMTER DONT KNOW WHY")
            break
        await asyncio.sleep(60)

# daily_reminder | returns what's due today and tomorrow
@tasks.loop(hours = 24)
async def daily_reminder(ctx):
    for i in range (1, int(len(IDS)/2+1), 1):
        channel_id = IDS["CHANNEL_ID_"+str(i)]
        channel = client.get_channel(channel_id) 
        assignment_count_today = 0
        assignment_count_tomorrow = 0
        inner_value_today = ""
        inner_value_tomorrow = ""
        today = strftime("%m-%d")
        course = canvas.get_course(IDS["COURSE_ID_"+str(i)])
        assignments = course.get_assignments(
            bucket = 'upcoming', 
            order_by = 'due_at')
        embed = discord.Embed(
        title = f"⏰ Daily Reminder {today}",
        color = 0xFFFF00)
        for i in assignments:
            if str(datetime.date.today()) == utc_to_pst(i.due_at_date, "no_include_hour"):
                assignment_count_today += 1 
                inner_value_today += f"{assignment_count_today}. {str(i)}\n"
            if str(datetime.date.today() + datetime.timedelta(days=1)) == utc_to_pst(i.due_at_date, "no_include_hour"): # find way to break after it fails
                assignment_count_tomorrow += 1
                inner_value_tomorrow += f"{assignment_count_tomorrow}. {str(i)}\n"
        if assignment_count_today > 0:
            embed.add_field(name = "Assignments Due Today", value = inner_value_today, inline = False)
        else:
            embed.add_field(name = "Assignments Due Today", value = "Nothing due today!", inline = False)
        if assignment_count_tomorrow > 0:
            embed.add_field(name = "Assignments Due Tomorrow", value = inner_value_tomorrow, inline = False)
        else:
            embed.add_field(name = "Assignments Due Tomorrow", value = "Nothing due tomorrow!", inline = False)
        embed.set_footer(text = "DISCLAIMNER: LAB DUE DATES ARE ONLY CORRECT FOR SECTION 8")
        await channel.send(embed=embed)

# -commands | returns list of commands
@client.command()
async def commands(ctx):
    embed = discord.Embed(
        title ="🐧 Commands",
        color = 0x68BBE3)
    embed.add_field(name = "-due", value = "returns an assignment that should be priortized as it will be due soon", inline = False)
    embed.add_field(name = "-assignments", value = "returns a list of all upcoming assignments", inline = False)
    embed.add_field(name = "-source", value = "returns a link to source code", inline = False)
    await ctx.send(embed=embed)

# -due | returns an upcoming assignment
@client.command()
async def due(ctx):
    channel_name = ctx.message.guild.name
    assignment = return_assignments(channel_name)[0]
    title_url = return_url(channel_name)
    date = utc_to_pst(assignment.due_at_date, "include_hour")
    lock_date = utc_to_pst(assignment.lock_at_date, "include_hour")
    points = assignment.points_possible
    description = assignment.description # returns HTML
    bad_characters = ["<span>", "</span>", "<ul>", "</ul>", "<li>", "</li>", "<strong>", "</strong>", "<p>", "</p>", "&nbsp", ";"]
    for i in bad_characters:
        description = description.replace(i, "")
    embed = discord.Embed(
        title = f"📅 {str(assignment)}",
        url = title_url,
        color = 0xF4364C)
    embed.add_field(name = f"Due: {date}", value = f"Locks at: {lock_date}\n"
                                                   f"Points: {points}\n"
                                                   f"\n{description}")

    await ctx.send(embed=embed)

# -assignments | returns list of assignments
@client.command()
async def assignments(ctx):
    channel_name = ctx.message.guild.name
    assignment_count = 0
    assignments = return_assignments(channel_name)
    title_url = return_url(channel_name)
    dates = []
    embed = discord.Embed(
        title ="📝 Assignments",
        url = title_url,
        color = 0x32CD30)
    for i in assignments: # combine into one loop ?
        dates.append(utc_to_pst(i.due_at_date, "include_hour"))
    for i in range(len(dates)):
        assignment_count += 1
        embed.add_field(name = f"{assignment_count}. {str(assignments[i])}", value = f"Due: {dates[i]}", inline = False)
    await ctx.send(embed=embed)

# -source | returns github
@client.command()
async def source(ctx):
    embed = discord.Embed(
        title ="🐈‍⬛ Source Code",
        description = 'If you have a suggestion or come across a bug, make an issue / pull request or message me',
        url = "https://github.com/BrandonAWong/canvas",
        color = 0x333)
    embed.set_footer(icon_url = "https://cdn.discordapp.com/attachments/1016129238862135396/1016151538923733012/unknown.png", text = "Brandon#4704")
    await ctx.send(embed=embed)

client.run(DISCORD_CLIENT)