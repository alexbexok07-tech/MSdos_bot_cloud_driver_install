import discord
from discord.ext import commands
import asyncio

class Schedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tasks = {}

    async def _lock_logic(self, channel, duration):
        try:
            await channel.set_permissions(channel.guild.default_role, send_messages=False)
            await channel.send(f"🔒 **[SCHEDULER]** Channel locked for {duration} minutes.")
            await asyncio.sleep(duration * 60)
            await channel.set_permissions(channel.guild.default_role, send_messages=True)
            await channel.send(f"🔓 **[SCHEDULER]** Timer expired. Channel unlocked.")
        except asyncio.CancelledError:
            pass
        finally:
            if channel.id in self.tasks:
                del self.tasks[channel.id]

    @commands.command(help="Locks a channel for a specific duration (minutes).")
    @commands.has_permissions(manage_channels=True)
    async def schedule_lock(self, ctx, channel: discord.TextChannel, duration: int):
        if channel.id in self.tasks:
            await ctx.send("⚠️ **[SCHEDULER]** A task is already running for this channel.")
            return
        task = asyncio.create_task(self._lock_logic(channel, duration))
        self.tasks[channel.id] = task
        await ctx.send(f"✅ **[SCHEDULER]** Lock scheduled for {channel.mention} ({duration}m).")

    @commands.command(help="Cancels a scheduled channel lock.")
    @commands.has_permissions(manage_channels=True)
    async def unschedule_lock(self, ctx, channel: discord.TextChannel):
        if channel.id in self.tasks:
            self.tasks[channel.id].cancel()
            await channel.set_permissions(channel.guild.default_role, send_messages=True)
            await ctx.send(f"✅ **[SCHEDULER]** Task for {channel.mention} cancelled.")
        else:
            await ctx.send("❌ **[SCHEDULER]** No active task found for this channel.")

async def setup(bot):
    await bot.add_cog(Schedule(bot))