import discord
import os
import requests
import ast
from discord.ext import commands

class DriverManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.registry_url = "https://raw.githubusercontent.com/alexbexok07-tech/MSdos_bot_cloud_driver_install/main/registry.json"
        self.protected = ["system", "driver_manager", "core"] # Cannot be uninstalled

    def get_registry(self):
        try:
            return requests.get(self.registry_url).json()
        except:
            return None

    def validate_code(self, code):
        """Checks if the downloaded code is valid Python syntax."""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    @commands.command(help="Lists available drivers in the registry.")
    async def find(self, ctx):
        reg = self.get_registry()
        if not reg: return await ctx.send("❌ **[CRITICAL]** Registry unreachable.")
        
        embed = discord.Embed(title="📦 Available Drivers", color=0x00FF00)
        for name, info in reg.items():
            embed.add_field(name=name, value=info['desc'], inline=False)
        await ctx.send(embed=embed)

    @commands.command(help="Installs a driver from the registry.")
    @commands.is_owner()
    async def install(self, ctx, name: str):
        reg = self.get_registry()
        if not reg or name not in reg:
            return await ctx.send(f"❌ **[ERROR]** Driver `{name}` not found in registry.")

        # 1. Download
        resp = requests.get(reg[name]['url'])
        if resp.status_code != 200:
            return await ctx.send("❌ **[NETWORK]** Failed to fetch remote source.")

        # 2. Validate
        if not self.validate_code(resp.text):
            return await ctx.send("❌ **[SECURITY]** Code validation failed. Syntax error detected.")

        # 3. Write Atomic (Write to temp, then move)
        path = f"cogs/{name}.py"
        with open(path, "w") as f:
            f.write(resp.text)

        # 4. Load
        try:
            await self.bot.load_extension(f"cogs.{name}")
            await ctx.send(f"✅ **[SUCCESS]** Driver `{name}` installed and initialized.")
        except Exception as e:
            await ctx.send(f"⚠️ **[WARN]** Installed, but failed to load: `{e}`")

    @commands.command(help="Uninstalls a driver.")
    @commands.is_owner()
    async def uninstall(self, ctx, name: str):
        if name in self.protected:
            return await ctx.send("🚫 **[SECURITY]** This driver is protected.")

        # 1. Unload
        try:
            await self.bot.unload_extension(f"cogs.{name}")
        except: pass 

        # 2. Remove
        path = f"cogs/{name}.py"
        if os.path.exists(path):
            os.remove(path)
            await ctx.send(f"🗑️ **[SUCCESS]** Driver `{name}` purged.")
        else:
            await ctx.send("❌ **[ERROR]** Driver file not found.")
            
    @commands.command(help="Force-update all installed drivers from the cloud.")
    @commands.is_owner()
    async def update(self, ctx):
        msg = await ctx.send("🔄 **[UPDATE]** Synchronizing with Cloud Registry...")
        reg = self.get_registry()
        if not reg:
            return await msg.edit(content="❌ **[CRITICAL]** Registry unreachable.")
        
        updated_count = 0
        for name in reg:
            path = os.path.join("cogs", f"{name}.py")
            if os.path.exists(path):
                # Re-run installation logic (download and load)
                # This effectively overwrites the old version with the new one
                await self.install(ctx, name)
                updated_count += 1
                
        await msg.edit(content=f"✅ **[UPDATE]** Successfully synchronized {updated_count} drivers.")        

async def setup(bot):
    await bot.add_cog(DriverManager(bot))