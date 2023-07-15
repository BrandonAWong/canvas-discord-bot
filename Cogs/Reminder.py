import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import random
from util import *


class Reminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open('./text/facts.txt', 'r') as file:
            self.facts = file.read().splitlines()
        with open('./text/quotes.txt', 'r') as file:
            self.quotes = file.read().splitlines()
        self.start_daily_reminder.start()

    @tasks.loop(minutes=1)
    async def start_daily_reminder(self) -> None:
        r: list[int] = []
        now: datetime = discord.utils.utcnow()
        server_ids: list[tuple] = return_server_ids()
        times: list[tuple] = return_times()

        for i, server in enumerate(server_ids):
            server = server[0]
            _now = convert_tz(server, now, '%H:%M')
            if _now == times[i][0] or True:
                r.append(server)

        await self.daily_reminder(r)

    async def daily_reminder(self, servers: list[int]) -> None:
        now: datetime = discord.utils.utcnow()
        
        for server in servers:
            today: str = convert_tz(server, now, '%Y-%m-%d')
            tomorrow: str = convert_tz(server, (now + timedelta(days=1)), '%Y-%m-%d')
            assignment_count_today = assignment_count_tomorrow = 0
            inner_value_today = inner_value_tomorrow = ''
            assignments = return_assignments(server)
            
            for assignment in assignments:
                due_date: str = convert_tz(
                    server,
                    assignment.due_at_date,
                    '%Y-%m-%d')
                
                due_hour: str = convert_tz(
                    server,
                    assignment.due_at_date,
                    '%I:%M %p')

                if today == due_date:
                    assignment_count_today += 1 
                    inner_value_today += (f'\n{assignment_count_today}. '
                                          f'{assignment.name}\n~  Due at {due_hour}\n')
                elif tomorrow == due_date:
                    assignment_count_tomorrow += 1
                    inner_value_tomorrow += (f'\n{assignment_count_tomorrow}. '
                                             f'{assignment.name}\n~  Due at {due_hour}\n')
                else:
                    break
                
            if assignment_count_today == 0:
                inner_value_today = 'Nothing due today 🥳'
            if assignment_count_tomorrow == 0:
                inner_value_tomorrow = 'Nothing due tomorrow 🤩'

            course = return_course(server).name
            embed = discord.Embed(
                title = f'⏰ {convert_tz(server, discord.utils.utcnow(), "%A %m-%d")}',
                color = 0xFFFF00)
            
            embed.add_field(
                name = course,
                value = '\n')
            
            embed.add_field(
                name = 'Assignments Due Today',
                value = inner_value_today, 
                inline = False)
            
            embed.add_field(
                name = 'Assignments Due Tomorrow', 
                value = inner_value_tomorrow, 
                inline = False)
            
            if random.randint(0,1) == 1:
                embed.set_footer(text = random.choice(self.facts))
            else:
                embed.set_footer(text = random.choice(self.quotes))
            
            try:
                channel_id = return_channel_id(server)
                channel = self.bot.get_channel(channel_id)
                await channel.send(embed=embed)
            except:
                pass

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Reminder(bot))