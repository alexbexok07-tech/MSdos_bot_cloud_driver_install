import discord
from discord.ext import commands
import requests
import socket

class Gate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Checks if a URL is responsive.")
    async def ping(self, ctx, url: str):
        try:
            response = requests.get(url, timeout=5)
            await ctx.send(f"📡 **[GATE]** {url} responded with status: **{response.status_code}**")
        except Exception as e:
            await ctx.send(f"❌ **[GATE]** Failed to reach {url}: {e}")

    @commands.command(help="Resolves a domain/host to an IP address.")
    async def whois(self, ctx, host: str):
        try:
            ip = socket.gethostbyname(host)
            await ctx.send(f"🌐 **[GATE]** Host `{host}` resolves to `{ip}`")
        except socket.gaierror:
            await ctx.send(f"❌ **[GATE]** Could not resolve host: {host}")

async def setup(bot):
    await bot.add_cog(Gate(bot))