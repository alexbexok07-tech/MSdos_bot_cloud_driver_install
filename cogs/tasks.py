import discord
from discord.ext import commands, tasks

class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup.start()

    @tasks.loop(hours=24)
    async def cleanup(self):
        # Example: Clear temp logs, restart certain modules, etc.
        print("[SYSTEM] Performing scheduled 24h maintenance.")

    def cog_unload(self):
        self.cleanup.cancel()

async def setup(bot):
    await bot.add_cog(Scheduler(bot))