from audioop import reverse
from xml.etree.ElementInclude import include
from canvasapi import Canvas
from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv
import os
import asyncio
import time

load_dotenv()

API_URL = "https://csulb.instructure.com/"
API_KEY = os.getenv("API_KEY")
DISCORD_CLIENT = os.getenv("DISCORD_CLIENT")

print(API_KEY)

canvas = Canvas(API_URL, API_KEY)
course_id = 3224

course = canvas.get_course(course_id)

announcements = canvas.get_announcements([course_id])

assignments = course.get_assignments(
    bucket = 'upcoming', 
    order_by = 'due_at')

def utc_to_pst(utc):
    date_format = '%m/%d %H:%M:%S %Z'
    date = utc.astimezone(timezone('US/Pacific'))
    return date.strftime(date_format)

date = assignments[0].due_at_date
print(f'{assignments[0]} is due {utc_to_pst(date)}')
