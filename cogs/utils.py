# -*- coding: utf-8 -*-

from discord.ext import commands
from datetime import datetime
from cogs.cog import Cog

class Utils(Cog):
    """The description for Utils goes here."""


    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')


    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! time is {ctx.bot.latency * 1000:.2f)} ms")

    @commands.command()
    async def time(self,ctx):
        await ctx.send(f'the time in alaska is {datetime.now().strftime("%a, %e %b %Y %H:%M:%S (%-I:%M %p)")}')


def setup(bot):
    bot.add_cog(Utils(bot))
