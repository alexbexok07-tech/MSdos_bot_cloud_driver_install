import discord
import os
from discord.ext import commands

# --- PAGINATION INTERFACE ---
class CommandPaginator(discord.ui.View):
    def __init__(self, commands_list, page_size=8):
        super().__init__(timeout=120)
        self.commands = commands_list
        self.page_size = page_size
        self.pages = [self.commands[i:i + page_size] for i in range(0, len(self.commands), page_size)]
        self.current_page = 0

    def get_embed(self):
        embed = discord.Embed(title=f"📦 Kernel Command Manifest ({self.current_page + 1}/{len(self.pages)})", color=0x00BFFF)
        for cmd in self.pages[self.current_page]:
            module_name = cmd.cog_name if cmd.cog_name else "Core"
            embed.add_field(name=f"*{cmd.name}", value=f"[{module_name}] {cmd.help or 'No description.'}", inline=False)
        return embed

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

# --- SYSTEM MANAGER ---
class SystemManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        raw_protected = os.environ.get('PROTECTED_MODULES', 'system,core')
        self.protected_modules = [m.strip().lower() for m in raw_protected.split(',')]

    def is_protected(self, module):
        return module.lower() in self.protected_modules

    @commands.command(help="Displays the command manifest.")
    async def cmds(self, ctx):
        all_commands = [c for c in self.bot.commands if not c.hidden]
        if not all_commands:
            return await ctx.send("❌ **[SYSTEM]** No commands found.")
        
        view = CommandPaginator(all_commands)
        await ctx.send(embed=view.get_embed(), view=view)

    @commands.command()
    @commands.is_owner()
    async def checkmodules(self, ctx):
        """Inventory report of all currently active modules."""
        extensions = [ext.replace("cogs.", "") for ext in self.bot.extensions.keys()]
        await ctx.send(f"**[INVENTORY]** Active Drivers: ```{', '.join(extensions)}```")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, module: str):
        """Reloads a specific module or all modules."""
        if module.lower() == "all":
            files = [f for f in os.listdir('./cogs') if f.endswith('.py') and f != '__init__.py']
            for filename in files:
                ext_name = f"cogs.{filename[:-3]}"
                if ext_name != "cogs.system": 
                    try:
                        await self.bot.reload_extension(ext_name)
                    except Exception as e:
                        print(f"[ERROR] Could not reload {ext_name}: {e}")
            
            await self.bot.reload_extension("cogs.system")
            await ctx.send("✅ **[SUCCESS]** All system drivers reloaded.")
        else:
            try:
                await self.bot.reload_extension(f'cogs.{module}')
                await ctx.send(f"✅ **[SUCCESS]** Driver [{module}] reloaded.")
            except Exception as e:
                await ctx.send(f"❌ **[ERROR]** {e}")
                
    @commands.command()
    @commands.is_owner()
    async def enable(self, ctx, module: str):
        """Enables/Loads a module or all modules."""
        if module.lower() == "all":
            files = [f[:-3] for f in os.listdir('./cogs') if f.endswith('.py') and f != '__init__.py']
            enabled = []
            for mod in files:
                ext_name = f"cogs.{mod}"
                if ext_name not in self.bot.extensions:
                    try:
                        await self.bot.load_extension(ext_name)
                        enabled.append(mod)
                    except Exception as e:
                        print(f"[ERROR] Failed to enable {mod}: {e}")
            
            summary = ", ".join(enabled) if enabled else "All drivers already active."
            await ctx.send(f"✅ **[SUCCESS]** Batch enable complete: `{summary}`")
        else:
            try:
                await self.bot.load_extension(f'cogs.{module}')
                await ctx.send(f"✅ **[SUCCESS]** Driver [{module}] enabled.")
            except Exception as e:
                await ctx.send(f"❌ **[ERROR]** {e}")

    @commands.command()
    @commands.is_owner()
    async def disable(self, ctx, module: str):
        """Disables/Unloads a module or all non-protected modules."""
        if module.lower() == "all":
            disabled = []
            loaded_exts = list(self.bot.extensions.keys())
            for ext in loaded_exts:
                mod_name = ext.replace("cogs.", "")
                if not self.is_protected(mod_name):
                    try:
                        await self.bot.unload_extension(ext)
                        disabled.append(mod_name)
                    except Exception as e:
                        print(f"[ERROR] Failed to unload {mod_name}: {e}")
            
            summary = ", ".join(disabled) if disabled else "No non-protected drivers to disable."
            await ctx.send(f"✅ **[SUCCESS]** Batch disable complete. Offline: `{summary}`")
        else:
            if self.is_protected(module):
                await ctx.send(f"⚠️ **[SECURITY]** Operation denied: Driver [{module}] is protected by root.")
                return

            try:
                await self.bot.unload_extension(f'cogs.{module}')
                await ctx.send(f"✅ **[SUCCESS]** Driver [{module}] offline.")
            except Exception as e:
                await ctx.send(f"❌ **[ERROR]** {e}")

async def setup(bot):
    await bot.add_cog(SystemManager(bot))