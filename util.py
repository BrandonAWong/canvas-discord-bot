from canvasapi import Canvas
from dotenv import load_dotenv
from pytz import timezone
import os


load_dotenv()
API_URL = 'https://csulb.instructure.com/'
API_KEY = os.getenv('API_KEY')
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