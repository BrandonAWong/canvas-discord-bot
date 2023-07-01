from canvasapi import Canvas
from pytz import timezone
import sqlite3


def create_connection() -> sqlite3.Connection | sqlite3.Cursor:
    con: sqlite3.Connection = sqlite3.connect('servers.db')
    cur: sqlite3.Cursor = con.cursor()
    return con, cur

def upload_row(server_id: int, org: str, course_id: int, token: str) -> None:
    con, cur = create_connection()
    if cur.execute(f"SELECT org FROM server WHERE server_id = {server_id}").fetchone():
        cur.execute(f"DELETE FROM server WHERE server_id = {server_id}")
    cur.execute("INSERT INTO server VALUES (?, ?, ?, ?)",
                (server_id, org, course_id, token))
    con.commit()
    con.close()

def create_canvas(server_id: int) -> Canvas:
    con, cur = create_connection()
    url, key = cur.execute("SELECT server_id, org, course_id, token"  
                           f"FROM server WHERE server_id = {server_id}")
    con.close()
    return Canvas(url, key)

def return_assignments(server_id) -> list:
    con, cur = create_connection()
    canvas = create_canvas(server_id)
    course_id: int = cur.execute("SELECT course_id FROM server" 
                        f"WHERE server_id = {server_id}")
    course = canvas.get_course(course_id)
    assignments = course.get_assignments(
        bucket = 'future', 
        order_by = 'due_at')
    con.close()
    return assignments

def return_url(server_id):
    con, cur = create_connection()
    org, id = cur.execute("SELECT org, course_id FROM server"
                                f"WHERE server_id = {server_id}")
    con.close()
    return f'https://{org}.instructure.com/courses/{id}/assignments'

def utc_to_pst(utc, format):
    if format == 'include_hour':
        date_format = '%m/%d %I:%M %p'
    elif format == 'only_hour':
        date_format = '%I:%M %p'
    else: 
        date_format = '%Y-%m-%d'
    date = utc.astimezone(timezone('US/Pacific'))
    return date.strftime(date_format)