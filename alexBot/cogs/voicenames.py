import logging
from typing import TYPE_CHECKING, Dict, List, Optional

import discord
from discord import app_commands

from ..tools import Cog

if TYPE_CHECKING:
    from bot import Bot


log = logging.getLogger(__name__)


class VoiceNames(Cog):
    namesGroup = app_commands.Group(name="names", description="Manage voice channel nicknames")

    # async def cog_load(self):
    #     self.bot.voiceCommandsGroup.add_command(self.namesGroup)

    # async def cog_unload(self):
    #     self.bot.voiceCommandsGroup.remove_command(self.namesGroup.name)

    @Cog.listener()
    async def on_voice_state_update(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ):
        if after.channel is None:
            return
        name = await self.bot.db.get_voice_name(after.channel.id, member.id)
        if name:
            await member.edit(nick=name)

    @namesGroup.command(name="set", description="Set a nickname for a user in a voice channel")
    async def set_name(
        self,
        interaction: discord.Interaction,
        channel: discord.VoiceChannel,
        name: str,
        member: Optional[discord.Member] = None,
    ):
        target = interaction.user
        if member and interaction.guild:
            if not interaction.user.guild_permissions.manage_nicknames:
                await interaction.response.send_message(
                    "You don't have permission to set nicknames for other users", ephemeral=True
                )
                return
            else:
                target = member
        await self.bot.db.save_voice_name(channel.id, target.id, name)
        await interaction.response.send_message(f"Set nickname for {target.mention} to {name} in {channel.mention}")

    @namesGroup.command(name="remove", description="Remove a nickname for a user in a voice channel")
    async def remove_name(
        self,
        interaction: discord.Interaction,
        channel: discord.VoiceChannel,
        member: Optional[discord.Member] = None,
    ):
        target = interaction.user
        if member and interaction.guild:
            if not interaction.user.guild_permissions.manage_nicknames:
                await interaction.response.send_message(
                    "You don't have permission to set nicknames for other users", ephemeral=True
                )
                return
            else:
                target = member
        await self.bot.db.delete_voice_name(channel.id, target.id)
        await interaction.response.send_message(f"Removed nickname for {target.mention} in {channel.mention}")


async def setup(bot: "Bot"):
    await bot.add_cog(VoiceNames(bot))
+