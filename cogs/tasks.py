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
        
    @commands.command(name="task_status", help="Check the current status of the background maintenance scheduler.")
    async def task_status(self, ctx):
        await ctx.send(f"⚙️ **[TASKS]** Background maintenance is active. Next cycle in: `{self.cleanup._next_iteration}`")    

    def cog_unload(self):
        self.cleanup.cancel()

async def setup(bot):
    await bot.add_cog(Scheduler(bot))
