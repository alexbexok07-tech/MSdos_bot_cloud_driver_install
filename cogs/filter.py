import discord
import os
from discord.ext import commands

class Filter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        raw_words = os.environ.get("BANNED_WORDS", "")
        self.banned_words = [word.strip().lower() for word in raw_words.split(",") if word.strip()]
        
        # Safely parse IGNORED_USER_IDS (Defaults to empty list if blank)
        raw_ignored = os.environ.get("IGNORED_USER_IDS", "")
        self.ignored_users = [int(x.strip()) for x in raw_ignored.split(",") if x.strip().isdigit()]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # 1. VIP Bypass Check
        if message.author.id in self.ignored_users:
            await self.bot.process_commands(message)
            return

        msg_content = message.content.lower()
        if any(word in msg_content for word in self.banned_words):
            # 2. Owner Bypass Check
            if await self.bot.is_owner(message.author):
                return
            
            try:
                await message.delete()
                # delete_after=4 prevents the bot's own warnings from clogging the chat!
                await message.channel.send(f"⚠️ **[FILTER]** Restricted content removed from {message.author.mention}.", delete_after=4)
            except Exception as e:
                print(f"[ERROR] Filter failed to execute strike: {e}")
            return

        await self.bot.process_commands(message)

    @commands.command(help="Adds a word to the filter list.")
    @commands.is_owner()
    async def addword(self, ctx, word: str):
        self.banned_words.append(word.lower())
        await ctx.send(f"✅ **[SUCCESS]** Added '{word}' to runtime filter.")

    @commands.command(help="Whitelists a User ID from the word filter for this session.")
    @commands.is_owner()
    async def ignoreuser(self, ctx, user_id: int):
        if user_id not in self.ignored_users:
            self.ignored_users.append(user_id)
            await ctx.send(f"🛡️ **[FILTER]** User `{user_id}` granted filter immunity.")
        else:
            await ctx.send(f"⚠️ **[FILTER]** User `{user_id}` is already immune.")

async def setup(bot):
    await bot.add_cog(Filter(bot))