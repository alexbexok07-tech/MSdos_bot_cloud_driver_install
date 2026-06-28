import os
import discord
from discord.ext import commands

class Audit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        raw_id = os.getenv("AUDIT_LOG_CHANNEL_ID")
        print(f"[DEBUG] Audit module loaded. Raw ID found: '{raw_id}'")
        
        if raw_id and raw_id.isdigit():
            self.log_channel_id = int(raw_id)
        else:
            self.log_channel_id = None
            print("[WARN] AUDIT_LOG_CHANNEL_ID is empty or invalid. Audit features disabled.") 

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if self.log_channel_id is None: return
        channel = self.bot.get_channel(self.log_channel_id)
        if channel:
            await channel.send(f"🗑️ **[AUDIT]** Message by {message.author} deleted in {message.channel}: '{message.content}'")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if self.log_channel_id is None: return
        channel = self.bot.get_channel(self.log_channel_id)
        if channel:
            await channel.send(f"👤 **[AUDIT]** {member.name} joined the environment.")

async def setup(bot):
    await bot.add_cog(Audit(bot))