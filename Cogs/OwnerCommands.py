from discord.ext import commands


class OwnerCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner() 
    async def sync(self, ctx: commands.Context) -> None:
        await self.bot.tree.sync()
        await ctx.reply('synced')

    @commands.command()
    @commands.is_owner() 
    async def clearTree(self, ctx: commands.Context) -> None:
        self.bot.tree.clear_commands(guild=None)
        await self.bot.tree.sync()
        await ctx.reply('cleared and synced')

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(OwnerCommands(bot))