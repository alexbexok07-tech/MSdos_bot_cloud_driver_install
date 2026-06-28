import discord
from discord.ext import commands

class EconomyHub(commands.Cog):
    # This flag tells main.py's global_restrictions to allow this Cog everywhere
    ignore_global_check = True 

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="economy_cmds", help="Display all available economy commands.")
    async def economy_cmds(self, ctx):
        embed = discord.Embed(
            title="💰 Economy Command Center",
            description="All financial tools are available below. These commands work in any channel.",
            color=0xFFD700 # Gold
        )
        
        # Hardcoding the list for a clean, professional appearance
        commands_list = [
            ("`*bal`", "Check your current wallet balance."),
            ("`*daily`", "Claim your free daily NG coins."),
            ("`*pay <user> <amount>`", "Transfer funds to another user."),
            ("`*gamble <amount>`", "Risk your NG on a coin flip."),
            ("`*lb`", "View the top 10 richest users.")
        ]
        
        for cmd, desc in commands_list:
            embed.add_field(name=cmd, value=desc, inline=False)
            
        embed.set_footer(text="MSdos.vxd | Financial System")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyHub(bot))
