import discord
import random
from discord.ext import commands

class TerminalGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hack")
    async def hack(self, ctx):
        await ctx.send("💻 **[TERMINAL]** Accessing firewall...")
        chance = random.randint(1, 100)
        if chance > 70:
            await ctx.send("✅ **[SUCCESS]** Root access gained. Data leaked: `7829-XJ-99`")
        else:
            await ctx.send("❌ **[FAILED]** Intrusion detected. IP Ban initiated.")

async def setup(bot):
    await bot.add_cog(TerminalGame(bot))