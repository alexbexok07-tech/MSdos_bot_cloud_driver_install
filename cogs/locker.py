import discord
from discord.ext import commands

class Locker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Locks a channel (disallows sending messages).")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        target = channel or ctx.channel
        try:
            await target.set_permissions(ctx.guild.default_role, send_messages=False)
            await ctx.send(f"✅ **[SUCCESS]** Channel {target.mention} is now locked.")
        except discord.Forbidden:
            await ctx.send("❌ **[ERROR]** Insufficient permissions to manage this channel.")

    @commands.command(help="Unlocks a channel (allows sending messages).")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        target = channel or ctx.channel
        try:
            await target.set_permissions(ctx.guild.default_role, send_messages=True)
            await ctx.send(f"✅ **[SUCCESS]** Channel {target.mention} is now unlocked.")
        except discord.Forbidden:
            await ctx.send("❌ **[ERROR]** Insufficient permissions to manage this channel.")

async def setup(bot):
    await bot.add_cog(Locker(bot))