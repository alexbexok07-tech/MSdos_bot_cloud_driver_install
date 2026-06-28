import discord
from discord.ext import commands

class Cache(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memory = {}

    @commands.command(name="push")
    async def push(self, ctx, key: str, *, content: str):
        self.memory[key] = content
        await ctx.send(f"💾 **[CACHE]** Data pushed to address `{key}`.")

    @commands.command(name="pull")
    async def pull(self, ctx, key: str):
        if key in self.memory:
            await ctx.send(f"📂 **[CACHE]** Retrieving `{key}`:\n```{self.memory[key]}```")
        else:
            await ctx.send("❌ **[ERROR]** Address not found.")

async def setup(bot):
    await bot.add_cog(Cache(bot))