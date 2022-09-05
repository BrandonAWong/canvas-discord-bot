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
CHANNEL_ID = 987096406214979634 # snowflake | change according to where you want messages to default
client = commands.Bot(command_prefix="-", intents=discord.Intents.all())


canvas = Canvas(API_URL, API_KEY)
COURSE_ID = 3224 # change COURSE_ID per course

course = canvas.get_course(COURSE_ID)
COURSE_ASSIGNMENTS_URL = f"{API_URL}courses/{COURSE_ID}/assignments"

# get assignment list | returns paginated list 
def return_assignments():
    assignments = course.get_assignments(
        bucket = 'upcoming', 
        order_by = 'due_at')
    return assignments

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
    while True: # repeat until 08:30
        if str(strftime("%H:%M")) == "00:27":
            daily_reminder.start(CHANNEL_ID)
            break
        await asyncio.sleep(60)

# daily_reminder | returns what's due today and tomorrow
@tasks.loop(seconds = 3)
async def daily_reminder(ctx):
    channel = client.get_channel(CHANNEL_ID) 
    assignment_count_today = 0
    assignment_count_tomorrow = 0
    inner_value_today = ""
    inner_value_tomorrow = ""
    today = strftime("%m-%d")
    embed = discord.Embed(
    title = f"⏰ Daily Reminder {today}",
    color = 0xFFFF00)
    for i in return_assignments():
        if str(datetime.date.today()) == utc_to_pst(i.due_at_date, "no_include_hour"):
            inner_value_today += str(i) + "\n"
            assignment_count_today += 1 
        if str(datetime.date.today() + datetime.timedelta(days=1)) == utc_to_pst(i.due_at_date, "no_include_hour"): # find way to break after it fails
            inner_value_tomorrow += str(i) + "\n"
            assignment_count_tomorrow += 1
    if assignment_count_today > 0:
        embed.add_field(name = "Assignments Due Today", value = inner_value_today, inline = False)
    else:
        embed.add_field(name = "Assignments Due Today", value = "Nothing due today!", inline = False)
    if assignment_count_tomorrow > 0:
        embed.add_field(name = "Assignments Due Tomorrow", value = inner_value_tomorrow, inline = False)
    else:
        embed.add_field(name = "Assignments Due Tomorrow", value = "Nothing due tomorrow!", inline = False)
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
    assignment = return_assignments()[0]
    date = utc_to_pst(assignment.due_at_date, "include_hour")
    lock_date = utc_to_pst(assignment.lock_at_date, "include_hour")
    points = assignment.points_possible
    description = assignment.description #returns HTML
    bad_characters = ["<span>", "</span>", "<ul>", "</ul>", "<li>", "</li>", "<strong>", "</strong>", "<p>", "</p>", "&nbsp", ";"]
    for i in bad_characters:
        description = description.replace(i, "")
    embed = discord.Embed(
        title ="💯 Upcoming Assignments",
        url = COURSE_ASSIGNMENTS_URL,
        color = 0xF4364C)
    embed.add_field(name = str(assignment), value = f"Due: {date}\n"
                                                    f"Locks at: {lock_date}\n"
                                                    f"Points: {points}\n"
                                                    f"\n{description}")

    await ctx.send(embed=embed)

# -assignments | returns list of assignments
@client.command()
async def assignments(ctx):
    assignments = return_assignments()
    dates = []
    embed = discord.Embed(
        title ="📝 Assignments",
        url = COURSE_ASSIGNMENTS_URL,
        color = 0x32CD30)
    for i in assignments:
        dates.append(utc_to_pst(i.due_at_date, "include_hour"))
    for i in range(len(dates)):
        embed.add_field(name = str(assignments[i]), value = f"Due: {dates[i]}", inline = False)
    await ctx.send(embed=embed)

# -source | returns github
@client.command()
async def source(ctx):
    embed = discord.Embed(
        title ="🐱‍👤 Source Code",
        description = 'If you have a suggestion or come across a bug, make a pull request or message me',
        url = "https://github.com/BrandonAWong/canvas",
        color = 0x333)
    embed.set_footer(icon_url = "https://cdn.discordapp.com/attachments/1016129238862135396/1016151538923733012/unknown.png", text = "Brandon#4704")
    await ctx.send(embed=embed)

client.run(DISCORD_CLIENT)