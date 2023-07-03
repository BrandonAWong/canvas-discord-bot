import discord
from discord.ext import commands, tasks
from time import strftime
import datetime
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
        if str(strftime('%H:%M')) == '08:30':
            self.daily_reminder.start()
            self.start_daily_reminder.cancel()

    @tasks.loop(hours=24)
    async def daily_reminder(self) -> None:
        server_ids: list[tuple] = return_server_ids()
        channel_ids: list[tuple] = return_channel_ids()
        for i in range(len(server_ids)):
            assignment_count_today = assignment_count_tomorrow = 0
            inner_value_today = inner_value_tomorrow = ''
            assignments = return_assignments(server_ids[i][0])
            for assignment in assignments:
                due_date = utc_to_pst(assignment.due_at_date, 'no_include_hour')
                due_hour = return_due_date(assignment)
                if str(datetime.date.today()) == due_date:
                    assignment_count_today += 1 
                    inner_value_today += (f'\n{assignment_count_today}. '
                                         f'{assignment.name}\n~  Due at {due_hour[-8:]}\n')
                elif str(datetime.date.today() + datetime.timedelta(days=1)) == due_date:
                    assignment_count_tomorrow += 1
                    inner_value_tomorrow += (f'\n{assignment_count_tomorrow}. '
                                             f'{assignment.name}\n~  Due at {due_hour[-8:]}\n')
                else:
                    break
                
            if assignment_count_today == 0:
                inner_value_today = 'Nothing due today 🥳'
            if assignment_count_tomorrow == 0:
                inner_value_tomorrow = 'Nothing due tomorrow 🤩'

            course = return_course(server_ids[i][0]).name
            embed = discord.Embed(
                title = f'⏰ {strftime("%A %m-%d")}',
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
            
            channel = self.bot.get_channel(channel_ids[i][0])
            await channel.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Reminder(bot))