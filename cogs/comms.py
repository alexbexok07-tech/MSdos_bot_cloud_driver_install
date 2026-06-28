import discord
from discord.ext import commands

class Comms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Forces the kernel to speak an official transmission.")
    @commands.is_owner()
    async def broadcast(self, ctx, channel: discord.TextChannel, *, raw_input: str):
        """Usage: *broadcast #general Title Here | Body text goes here"""
        if "|" in raw_input:
            title, body = raw_input.split("|", 1)
        else:
            title = "SYSTEM NOTICE"
            body = raw_input

        embed = discord.Embed(
            title=f"📢 // {title.strip()}",
            description=body.strip(),
            color=0xFF4500 # Cyberpunk Neon Orange
        )
        embed.set_footer(text="VERIFIED KERNEL TRANSMISSION")

        await channel.send(embed=embed)
        await ctx.send(f"✅ **[COMMS]** Uplink dispatched to {channel.mention}", delete_after=3)

    @commands.command(help="Silently repeats your text and deletes your command prompt.")
    @commands.is_owner()
    async def echo(self, ctx, *, message: str):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(Comms(bot))