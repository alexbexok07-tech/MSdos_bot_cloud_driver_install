import discord
from discord.ext import commands
import psutil

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="proc")
    async def proc_stats(self, ctx):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        await ctx.send(f"⚙️ **[HARDWARE]** CPU: `{cpu}%` | RAM: `{mem}%`")

async def setup(bot):
    await bot.add_cog(Status(bot))