import discord
from discord.ext import commands, tasks
from datetime import date, timedelta
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
        r: list = []
        now = discord.utils.utcnow()
        now: str = now.strftime('%H:%M')
        server_ids: list[tuple] = return_server_ids()
        times: list[tuple] = return_times()
        for i in range(len(server_ids)):
            if now == times[i][0]:
                r.append(server_ids[i][0])
        await self.daily_reminder(r)

    async def daily_reminder(self, servers: list) -> None:
        channel_ids: list = return_channel_ids(servers)
        for i in range(len(servers)):
            assignment_count_today = assignment_count_tomorrow = 0
            inner_value_today = inner_value_tomorrow = ''
            server_id: int = servers[i]
            assignments = return_assignments(server_id)
            for assignment in assignments:
                due_date: str = assignment.due_at_date.strftime('%Y-%m-%d')
                due_hour: str = return_due_hour(assignment)
                if str(date.today()) == due_date:
                    assignment_count_today += 1 
                    inner_value_today += (f'\n{assignment_count_today}. '
                                         f'{assignment.name}\n~  Due at {due_hour}\n')
                elif str(date.today() + timedelta(days=1)) == due_date:
                    assignment_count_tomorrow += 1
                    inner_value_tomorrow += (f'\n{assignment_count_tomorrow}. '
                                             f'{assignment.name}\n~  Due at {due_hour}\n')
                else:
                    break
                
            if assignment_count_today == 0:
                inner_value_today = 'Nothing due today 🥳'
            if assignment_count_tomorrow == 0:
                inner_value_tomorrow = 'Nothing due tomorrow 🤩'

            course = return_course(server_id).name
            embed = discord.Embed(
                title = f'⏰ {convert_tz(server_id, discord.utils.utcnow(), "%A %m-%d")}',
                color = 0xFFFF00)
            embed.add_field(name = course,
                            value = '\n')
            embed.add_field(name = 'Assignments Due Today',
                            value = inner_value_today, 
                            inline = False)
            embed.add_field(name = 'Assignments Due Tomorrow', 
                            value = inner_value_tomorrow, 
                            inline = False)
            
            if random.randint(0,1) == 1:
                embed.set_footer(text = random.choice(self.facts))
            else:
                embed.set_footer(text = random.choice(self.quotes))
            
            channel = self.bot.get_channel(channel_ids[i])
            await channel.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Reminder(bot))