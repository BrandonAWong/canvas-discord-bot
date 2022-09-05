from canvasapi import Canvas
from datetime import datetime
from pytz import timezone
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = "https://csulb.instructure.com/"
API_KEY = os.getenv("API_KEY")

DISCORD_CLIENT = os.getenv("DISCORD_CLIENT")
client = commands.Bot(command_prefix="-", intents=discord.Intents.all())

canvas = Canvas(API_URL, API_KEY)
course_id = 3224

course = canvas.get_course(course_id)
course_assignments_url = f"{API_URL}courses/{course_id}/assignments"

date_format = '%m/%d %H:%M'

# announcements = canvas.get_announcements([course_id])

def return_assignments():
    assignments = course.get_assignments(
        bucket = 'upcoming', 
        order_by = 'due_at')
    return assignments

def utc_to_pst(utc):
    date = utc.astimezone(timezone('US/Pacific'))
    return date.strftime(date_format)

#work on this
def check_due():
    return

# on join
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

# -commands | returns list of commands
@client.command()
async def commands(ctx):
    embed = discord.Embed(
    title="Commands",
    color = 0x68BBE3)
    embed.add_field(name = "-due", value = "returns an assignment that should be priortized as it will be due soon", inline = False)
    embed.add_field(name = "-assignments", value = "returns a list of upcoming assignments", inline = False)
    embed.add_field(name = "-source", value = "returns a link to source code", inline = False)
    await ctx.send(embed=embed)

# -due | returns an upcoming assignment
@client.command()
async def due(ctx):
    assignment = return_assignments()[0]
    date = utc_to_pst(assignment.due_at_date)
    lock_date = utc_to_pst(assignment.lock_at_date)
    points = assignment.points_possible
    description = assignment.description #returns HTML
    bad_characters = ["<span>", "</span>", "<ul>", "</ul>", "<li>", "</li>", "<strong>", "</strong>", "<p>", "</p>", "&nbsp", ";"]
    for i in bad_characters:
        description = description.replace(i, "")
    embed = discord.Embed(
    title="Upcoming Assignments",
    url = course_assignments_url,
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
    title="Upcoming Assignments",
    url = course_assignments_url,
    color = 0x32CD30)
    for i in assignments:
        dates.append(utc_to_pst(i.due_at_date))
    for i in range(len(dates)):
        embed.add_field(name = str(assignments[i]), value = f"Due: {dates[i]}", inline = False)
    await ctx.send(embed=embed)

# -source | returns github
@client.command()
async def source(ctx):
    embed = discord.Embed(
    title="Source",
    description = 'If you have a suggestion or come across a bug, make a pull request or message me',
    url = "https://github.com/BrandonAWong/canvas",
    color = 0x333)
    embed.set_footer(icon_url = "https://cdn.discordapp.com/attachments/1016129238862135396/1016129321594781766/pq34_-_Copy.jpg", text = "Brandon#4704")
    await ctx.send(embed=embed)


client.run(DISCORD_CLIENT)
