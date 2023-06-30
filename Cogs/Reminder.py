import discord
from discord.ext import commands, tasks
from time import strftime
import datetime
import asyncio
import random
from util import *


class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('./text/facts.txt', 'r') as file:
            self.facts = file.read().splitlines()
        with open('./text/quotes.txt', 'r') as file:
            self.quotes = file.read().splitlines()

    async def check_daily_reminder(self):
        while True: 
            if str(strftime('%H:%M')) == '16:30':
                self.daily_reminder.start('hello')
                break
            await asyncio.sleep(60)

    @tasks.loop(hours=24)
    async def daily_reminder(self, ctx):
        for i in range (1, int(len(IDS)/2+1)):
            channel_id = IDS['CHANNEL_ID_'+str(i)]
            channel = self.bot.get_channel(channel_id) 
            assignment_count_today = assignment_count_tomorrow = 0
            inner_value_today = inner_value_tomorrow = ''
            course = canvas.get_course(IDS['COURSE_ID_'+str(i)])
            assignments = course.get_assignments(
                bucket = 'upcoming', 
                order_by = 'due_at')
            
            for assignment in assignments:
                due_date = utc_to_pst(assignment.due_at_date, 'no_include_hour')
                due_hour = str(utc_to_pst(assignment.due_at_date, 'only_hour'))
                if str(datetime.date.today()) == due_date:
                    assignment_count_today += 1 
                    inner_value_today += f'\n{assignment_count_today}. {str(assignment)}\n~  Due at {due_hour}\n'
                elif str(datetime.date.today() + datetime.timedelta(days=1)) == due_date:
                    assignment_count_tomorrow += 1
                    inner_value_tomorrow += f'\n{assignment_count_tomorrow}. {str(assignment)}\n~  Due at {due_hour}\n'
                else:
                    break
                
            if assignment_count_today == 0:
                inner_value_today = 'Nothing due today 🥳'
            if assignment_count_tomorrow == 0:
                inner_value_tomorrow = 'Nothing due tomorrow 🎉'

            embed = discord.Embed(
                title = f'⏰ {strftime("%A %m-%d")}',
                color = 0xFFFF00)
            embed.add_field(name = 'Assignments Due Today', value = inner_value_today, inline = False)
            embed.add_field(name = 'Assignments Due Tomorrow', value = inner_value_tomorrow, inline = False)
            
            if random.randint(0,1) == 1:
                embed.set_footer(text = random.choice(self.facts))
            else:
                embed.set_footer(text = random.choice(self.facts))
            await channel.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Reminder(bot))