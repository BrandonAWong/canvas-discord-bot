from canvasapi import Canvas
from pytz import timezone
from datetime import datetime
import sqlite3

def create_connection() -> sqlite3.Connection | sqlite3.Cursor:
    con: sqlite3.Connection = sqlite3.connect('servers.db', timeout=10)
    cur: sqlite3.Cursor = con.cursor()
    return con, cur

def upload_row(server_id: int, channel_id: int, org: str, course_id: int, token: str) -> bool:
    con, cur = create_connection()
    preexist = False

    if cur.execute("SELECT org FROM server WHERE server_id = (?)", (server_id, )).fetchone():
        preexist = True
        cur.execute(
            ("UPDATE server SET server_id = (?), channel_id = (?),"
            "org = (?), course_id = (?), token = (?)  WHERE server_id = (?)"),
            (server_id, channel_id, org, course_id, token, server_id))
    else:
        cur.execute(
            "INSERT INTO server VALUES (?, ?, ?, ?, ?)",
            (server_id, channel_id, org, course_id, token))
        
        cur.execute(
            "INSERT INTO time VALUES (?, ?, ?)",
            (server_id, '08:30', 'UTC'))
        
    con.commit()
    con.close()

    if validate_upload(server_id):
        return True
    else:
        if not preexist:
            delete_server(server_id)
        return False

def validate_upload(server_id: int) -> bool:
    try:
        return_course(server_id)
        return True
    except:
        return False

def update_time(server_id: int, time: str) -> bool:
    con, cur = create_connection()

    cur.execute(
        "UPDATE time SET time = (?) WHERE server_id = (?)",
        (time, server_id))
    
    if validate_time(time):
        con.commit()
        con.close()
        return True
    else:
        con.close()
        return False

def validate_time(time) -> bool:
    if len(time) != 5:
        return False
    
    try:
        datetime.strptime(time, '%H:%M')
        return True
    except:
        return False

def update_time_zone(server_id: int, tz: str) -> bool:
    con, cur = create_connection()

    cur.execute(
        "UPDATE time SET time_zone = (?) WHERE server_id = (?)",
        (tz, server_id))
    
    if validate_time_zone(tz):
        con.commit()
        con.close()
        return True
    else:
        con.close()
        return False

def validate_time_zone(tz) -> bool:
    try:
        datetime.now().astimezone(timezone(tz))
        return True
    except:
        return False

def delete_server(server_id) -> None:
    con, cur = create_connection()
    
    cur.execute(
        "DELETE FROM server WHERE server_id = (?)", 
        (server_id, ))
    
    cur.execute(
        "DELETE FROM time WHERE server_id = (?)", 
        (server_id, ))
    
    con.commit()
    con.close()

def return_server_ids() -> list[tuple]:
    con, cur = create_connection()
    res = cur.execute("SELECT server_id FROM server")
    info = res.fetchall()
    con.close()
    return info

def return_channel_id(server_id=None) -> int:
    con, cur = create_connection()

    res = cur.execute(
        "SELECT channel_id FROM server WHERE server_id = (?)",
        (server_id, ))
    
    channel = res.fetchone()[0]
    con.close()
    return channel

def return_times() -> list[tuple]:
    con, cur = create_connection()
    res = cur.execute("SELECT time FROM time")
    info = res.fetchall()
    con.close()
    return info

def create_canvas(server_id: int) -> Canvas:
    con, cur = create_connection()

    res = cur.execute(
        "SELECT org, token FROM server WHERE server_id = (?)", 
        (server_id, ))
    
    org, key = res.fetchone()
    url = f'https://{org}.instructure.com/'
    con.close()
    return Canvas(url, key)

def return_course(server_id: int):
    con, cur = create_connection()
    canvas = create_canvas(server_id)

    res = cur.execute(
        "SELECT course_id FROM server WHERE server_id = (?)",
        (server_id, ))
    
    course_id: int = res.fetchone()[0]
    course = canvas.get_course(course_id)
    con.close()
    return course

def return_assignments(server_id: int) -> list:
    course = return_course(server_id)
    assignments = course.get_assignments(
        bucket = 'upcoming', 
        order_by = 'due_at')
    return assignments

def return_assignments_url(server_id: int) -> str:
    con, cur = create_connection()

    res = cur.execute(
        "SELECT org, course_id FROM server WHERE server_id = (?)", 
        (server_id, ))
    
    org, id = res.fetchone()
    con.close()
    return f'https://{org}.instructure.com/courses/{id}/assignments'

def convert_tz(server_id: int, utc: datetime, format: str) -> str:
    tz = return_timezone(server_id)
    date = utc.astimezone(timezone(tz))
    return date.strftime(format)

def return_timezone(server_id: int) -> str:
    con, cur = create_connection()

    res = cur.execute(
        "SELECT time_zone FROM time WHERE server_id = (?)", 
        (server_id, ))
    
    tz = res.fetchone()
    con.close()
    return tz[0]