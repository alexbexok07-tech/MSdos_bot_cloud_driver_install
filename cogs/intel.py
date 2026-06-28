import discord
from discord.ext import commands

class Intel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activity_map = {} # {user_id: count}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        self.activity_map[message.author.id] = self.activity_map.get(message.author.id, 0) + 1

    @commands.command(name="intel")
    async def get_intel(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        count = self.activity_map.get(target.id, 0)
        await ctx.send(f"📊 **[INTEL]** {target.name} has transmitted `{count}` packets (messages) to this sector.")

async def setup(bot):
    await bot.add_cog(Intel(bot))