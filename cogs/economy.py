import discord
import json
import os
import random
from discord.ext import commands

# SYSTEM CONFIG
NG_EMOJI = "<:ngcoin:1520751952428924978>"

class Economy(commands.Cog):
    # This attribute allows main.py to identify this cog as channel-agnostic
    ignore_global_check = True 

    def __init__(self, bot):
        self.bot = bot
        self.db_file = "economy.json"
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, "r") as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open(self.db_file, "w") as f:
            json.dump(self.data, f, indent=4)

    # --- CORE UTILS ---
    def get_balance(self, user_id):
        return self.data.get(str(user_id), 0)

    # --- COMMANDS ---
    @commands.command(help="Check your balance or another user's.")
    async def bal(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        balance = self.get_balance(target.id)
        
        embed = discord.Embed(title=f"💳 {target.name}'s Account", color=0x00FF00)
        embed.add_field(name="Current Balance", value=f"{NG_EMOJI} **{balance:,} $NG**")
        await ctx.send(embed=embed)

    @commands.command(help="Claim 100 $NG daily.")
    async def daily(self, ctx):
        user_id = str(ctx.author.id)
        self.data[user_id] = self.get_balance(user_id) + 100
        self.save_data()
        await ctx.send(f"✅ **[ECONOMY]** {ctx.author.mention} claimed 100 {NG_EMOJI} $NG. Your total: **{self.get_balance(user_id):,}**")

    @commands.command(help="Transfer $NG to another user.")
    async def pay(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ **[ECONOMY]** You must send a positive amount.")
        if member == ctx.author:
            return await ctx.send("❌ **[ECONOMY]** You cannot pay yourself.")
        
        sender_bal = self.get_balance(ctx.author.id)
        if sender_bal < amount:
            return await ctx.send(f"❌ **[ECONOMY]** Insufficient funds. You only have {sender_bal:,} {NG_EMOJI}.")

        self.data[str(ctx.author.id)] -= amount
        self.data[str(member.id)] = self.get_balance(member.id) + amount
        self.save_data()
        
        await ctx.send(f"💸 **[ECONOMY]** Transferred {amount:,} {NG_EMOJI} to {member.mention}.")

    @commands.command(help="Gamble your $NG coins.")
    async def gamble(self, ctx, amount: int):
        if amount > self.get_balance(ctx.author.id):
            return await ctx.send("❌ **[ECONOMY]** You don't have enough to gamble.")
        
        if random.choice([True, False]): 
            self.data[str(ctx.author.id)] += amount
            await ctx.send(f"🎉 **[WIN]** You won {amount:,} {NG_EMOJI}! Your total: **{self.get_balance(ctx.author.id):,}**")
        else: 
            self.data[str(ctx.author.id)] -= amount
            await ctx.send(f"💀 **[LOSS]** You lost {amount:,} {NG_EMOJI}. Your total: **{self.get_balance(ctx.author.id):,}**")
        self.save_data()

    @commands.command(help="View the global leaderboard.")
    async def lb(self, ctx):
        sorted_users = sorted(self.data.items(), key=lambda item: item[1], reverse=True)[:10]
        
        embed = discord.Embed(title=f"🏆 {ctx.guild.name} Wealth Leaderboard", color=0xFFD700)
        for idx, (uid, bal) in enumerate(sorted_users, 1):
            user = self.bot.get_user(int(uid))
            name = user.name if user else f"Unknown ({uid})"
            embed.add_field(name=f"{idx}. {name}", value=f"{bal:,} {NG_EMOJI}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(help="Add $NG coins (Admin only).")
    @commands.is_owner()
    async def addcoins(self, ctx, member: discord.Member, amount: int):
        self.data[str(member.id)] = self.get_balance(member.id) + amount
        self.save_data()
        await ctx.send(f"🔨 **[ADMIN]** Added {amount:,} {NG_EMOJI} to {member.name}.")

async def setup(bot):
    await bot.add_cog(Economy(bot))