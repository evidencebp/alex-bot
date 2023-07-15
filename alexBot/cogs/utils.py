# -*- coding: utf-8 -*-

import asyncio
import datetime
import random
from dataclasses import dataclass
from typing import List, Optional

import discord
import humanize
from discord import app_commands
from discord.ext import commands
from discord.member import VoiceState

from ..tools import Cog

DATEFORMAT = "%a, %e %b %Y %H:%M:%S (%-I:%M %p)"


@dataclass
class Roll:
    dice: str
    rolls: List[int]

    def __str__(self):
        return f"{self.dice}: {', '.join([str(r) for r in self.rolls])}"


class Utils(Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.current_thatars = []

    async def cog_load(self):
        self.bot.voiceCommandsGroup.add_command(
            app_commands.Command(
                name="move",
                description="Moves the current group to another voice channel.",
                callback=self.voice_move,
            )
        )
        self.bot.voiceCommandsGroup.add_command(
            app_commands.Command(
                name="theatre",
                description="create a temporary channel for watching videos with friends",
                callback=self.voice_theatre,
            )
        )

    async def cog_unload(self):
        self.bot.voiceCommandsGroup.remove_command("move")
        self.bot.voiceCommandsGroup.remove_command("theatre")

    @app_commands.command()
    @app_commands.describe(dice="dice format in XdY. can be multiple sets, seperated by spaces")
    async def roll(self, interaction: discord.Interaction, dice: str):
        """Rolls a dice in NdN format."""
        roll_results: List[Roll] = []
        for rollset in dice.split(" "):
            try:
                rolls, limit = map(int, rollset.split("d"))
                if rolls > 100:
                    return await interaction.response.send_message(
                        "You can't roll more than 100 dice at once!", ephemeral=True
                    )
            except Exception:
                return await interaction.response.send_message("Format has to be in `WdX YdZ`...!", ephemeral=True)
            roll_results.append(Roll(f"{rolls}d{limit}", [random.randint(1, limit) for r in range(rolls)]))

        result = "\n".join([str(r) for r in roll_results])
        raw_results = []
        for roll in roll_results:
            [raw_results.append(r) for r in roll.rolls]

        result += f"\n\nTotal: {sum(raw_results)}"
        result += f"\nAverage: {sum(raw_results) / len(raw_results)}"
        result += f"\nMax: {max(raw_results)}"
        result += f"\nMin: {min(raw_results)}"
        try:
            await interaction.response.send_message(result, ephemeral=False)
        except discord.HTTPException:
            await interaction.response.send_message("Result too long!", ephemeral=True)

    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.checks.has_permissions(manage_channels=True)
    async def voice_theatre(self, interaction: discord.Interaction, name: Optional[str]):
        if name is None:
            name = "Theatre"
        target_catagory = None
        if interaction.user.voice:
            # we have a voice channel, is it in a category?
            if interaction.user.voice.channel.category:
                target_catagory = interaction.user.voice.channel.category
        if target_catagory is None:
            # if the current channel is in a catagory, put it there
            target_catagory = interaction.channel.category

        chan = await interaction.guild.create_voice_channel(name=name, category=target_catagory)
        self.current_thatars.append(chan.id)
        await interaction.response.send_message(f"Created a new theatre channel, {chan.mention}", ephemeral=False)
        await asyncio.sleep(5 * 60)
        try:
            chan: discord.VoiceChannel = await self.bot.fetch_channel(chan.id)
            if chan is not None:
                if len(chan.members) == 0:
                    await chan.delete()
        except discord.NotFound:
            pass

    @commands.command(aliases=['diff'])
    async def difference(self, ctx: commands.Context, one: discord.Object, two: Optional[discord.Object] = None):
        """Compares the creation time of two IDs. default to comparing to the current time."""
        two = two or ctx.message
        if two is None:
            two = ctx.message
        else:
            now = False

        if one.created_at > two.created_at:
            earlier_first = False
            diff = one.created_at.replace(tzinfo=datetime.timezone.utc) - two.created_at.replace(
                tzinfo=datetime.timezone.utc
            )
        else:
            earlier_first = True
            diff = two.created_at.replace(tzinfo=datetime.timezone.utc) - one.created_at.replace(
                tzinfo=datetime.timezone.utc
            )

        embed = discord.Embed()
        embed.add_field(
            name=f"{'Earlier' if earlier_first else 'Later'} (`{one.id}`)",
            value=f"`{one.created_at.replace(tzinfo=datetime.timezone.utc)}`, <t:{one.created_at.replace(tzinfo=datetime.timezone.utc).timestamp():.0f}> - <t:{one.created_at.replace(tzinfo=datetime.timezone.utc).timestamp():.0f}:R>",
        )
        embed.add_field(
            name=f"{'Later' if earlier_first else 'Earlier'} (`{two.id}`)",
            value=f"`{two.created_at.replace(tzinfo=datetime.timezone.utc)}`, <t:{two.created_at.replace(tzinfo=datetime.timezone.utc).timestamp():.0f}> -  <t:{two.created_at.replace(tzinfo=datetime.timezone.utc).timestamp():.0f}:R>",
        )
        embed.add_field(name="Difference", value=f"`{diff}` ({humanize.naturaldelta(diff)})")

        await ctx.send(embed=embed)

    @commands.command(name='info', aliases='source about git'.split())
    async def info(self, ctx):
        """general bot information"""
        ret = discord.Embed()
        ret.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        ret.add_field(name='Support Server', value='[link](https://discord.gg/jMwPFqp)')
        ret.add_field(name='Source Code', value='[github](https://github.com/mralext20/alex-bot)')
        ret.add_field(name='Servers', value=str(len(self.bot.guilds)))
        ret.add_field(name='Members', value=str(len(list(self.bot.get_all_members()))))
        await ctx.send(embed=ret)

    @commands.command(name='inviteDetails')
    async def inviteDetails(self, ctx, invite: discord.Invite):
        """Tells you about an invite, such as how many members the server it's pointed to has and more!"""
        if invite.revoked:
            return await ctx.send("That invite is revoked...")
        ret = discord.Embed()
        ret.set_thumbnail(url=invite.guild.icon.url)
        ret.title = invite.guild.name
        ret.add_field(name='aprox members', value=invite.approximate_member_count, inline=True)
        ret.add_field(name='Aprox Present Members', value=invite.approximate_presence_count, inline=True)
        ret.add_field(name='guild created at', value=invite.guild.created_at, inline=True)
        ret.add_field(name='guild ID', value=invite.guild.id, inline=True)
        ret.add_field(name='verification level', value=invite.guild.verification_level, inline=True)
        if invite.guild.features:
            ret.add_field(name='features:', value=', '.join(invite.guild.features), inline=False)
        if invite.inviter:
            ret.add_field(name='inviter name', value=invite.inviter.name, inline=True)
            ret.add_field(name='inviter id', value=invite.inviter.id, inline=True)
        if invite.channel:
            ret.add_field(name='channel target', value=invite.channel.name, inline=True)
            ret.add_field(name='channel Type', value=invite.channel.type, inline=True)

        await ctx.send(embed=ret)

    @commands.command()
    async def invite(self, ctx):
        """tells you my invite link!"""
        await ctx.send(
            f"<https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot%20applications.commands>"
        )

    @app_commands.checks.bot_has_permissions(move_members=True)
    @app_commands.checks.has_permissions(move_members=True)
    @app_commands.describe(target="the voice channel to move everyone to")
    async def voice_move(self, interaction: discord.Interaction, target: discord.VoiceChannel):
        if not interaction.user.voice:
            return await interaction.response.send_message("you must be in a voice call!", ephemeral=True)
        await interaction.response.defer()
        for user in interaction.user.voice.channel.members:
            asyncio.get_event_loop().create_task(user.move_to(target, reason=f"as requested by {interaction.user}"))
        await interaction.followup.send(":ok_hand:", ephemeral=True)

    @Cog.listener()
    async def on_voice_state_update(self, member, before: Optional[VoiceState], after: Optional[VoiceState]):
        if not (after is None or after.channel is None):
            if after.channel.id == 889031486978785312:
                # check for existing instance and close
                if (not after.channel.guild.voice_client) or (not after.channel.guild.voice_client.is_connected()):
                    vc = await after.channel.connect()
                    vc.play(
                        discord.PCMVolumeTransformer(
                            discord.FFmpegPCMAudio("https://retail-music.com/walmart_radio.mp3")
                        )
                    )
                    vc.source.volume = 0.25
        if before.channel.id in self.current_thatars:
            if len(before.channel.members) == 0:
                await before.channel.delete(reason="no one left")
                self.current_thatars.remove(before.channel.id)


async def setup(bot):
    await bot.add_cog(Utils(bot))
