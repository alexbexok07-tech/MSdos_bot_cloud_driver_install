import discord
from discord.ext import commands

class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Checks if the Tools driver is responsive.")
    async def hello(self, ctx):
        await ctx.send("Driver [Tools] is operational.")

async def setup(bot):
    await bot.add_cog(Tools(bot))