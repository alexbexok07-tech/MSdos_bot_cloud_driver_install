import discord
from discord.ext import commands

class Remote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fwd")
    @commands.is_owner()
    async def forward(self, ctx, channel_id: int, *, msg: str):
        target = self.bot.get_channel(channel_id)
        if target:
            await target.send(msg)
            await ctx.send(f"✅ Sent to `{target.name}`.")
        else:
            await ctx.send("❌ Channel not found.")

async def setup(bot):
    await bot.add_cog(Remote(bot))