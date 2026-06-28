import discord
from discord.ext import commands
import time

class Deduplicator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Format: { (channel_id, content): timestamp }
        self.history = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        # Only check messages from the bot itself
        if message.author != self.bot.user:
            return

        # Create a unique key for this message
        key = (message.channel.id, message.content)
        now = time.time()

        # Check if we saw this message within the last 5 seconds
        if key in self.history and (now - self.history[key] < 5):
            try:
                # This is the "kill" command
                await message.delete()
            except Exception as e:
                pass
            return

        # Otherwise, save this message to history
        self.history[key] = now

async def setup(bot):
    await bot.add_cog(Deduplicator(bot))