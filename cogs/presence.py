import discord
from discord.ext import commands, tasks
import itertools

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.statuses = itertools.cycle([
            discord.Activity(type=discord.ActivityType.listening, name="*system diagnostics"),
            discord.Activity(type=discord.ActivityType.watching, name="SECTOR // 01 traffic"),
            discord.Activity(type=discord.ActivityType.playing, name="MSdos.vxd // kernel.sys"),
        ])

    async def cog_load(self):
        self.status_loop.start()

    def cog_unload(self):
        self.status_loop.cancel()

    @tasks.loop(minutes=12)
    async def status_loop(self):
        await self.bot.change_presence(activity=next(self.statuses), status=discord.Status.online)

    @status_loop.before_loop
    async def before_status_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Presence(bot))