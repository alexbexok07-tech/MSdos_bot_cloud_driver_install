import discord
from discord.ext import commands
import time
import platform

class CoreDriver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.command(name="system")
    async def system_diagnostics(self, ctx):
        """Displays the current health and latency of the kernel."""
        latency = round(self.bot.latency * 1000)
        
        current_time = time.time()
        uptime_seconds = int(current_time - self.start_time)
        days, rem = divmod(uptime_seconds, 86400)
        hours, minutes = divmod(rem, 3600)
        uptime_str = f"{days}d {hours}h {minutes}m"

        host_os = f"{platform.system()} {platform.release()}"
        python_version = platform.python_version()

        embed = discord.Embed(
            title="MSdos.vxd/Kernel // UNIT 01 status",
            description="```diff\n+ SECURE / UNRESTRICTED ACCESS GRANTED\n```",
            color=discord.Color.from_rgb(255, 0, 0)
        )
        
        embed.add_field(name="📡 SYSTEM LATENCY", value=f"```\n{latency} ms\n```", inline=True)
        embed.add_field(name="⏳ KERNEL UPTIME", value=f"```\n{uptime_str}\n```", inline=True)
        embed.add_field(name="☁️ HOST PLATFORM", value=f"```\n{host_os}\n```", inline=False)
        embed.add_field(name="🐍 PYTHON vXD", value=f"```yaml\n{python_version}\n```", inline=True)
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url)
        embed.set_footer(text=f"Requested by root@{ctx.author.name}")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CoreDriver(bot))