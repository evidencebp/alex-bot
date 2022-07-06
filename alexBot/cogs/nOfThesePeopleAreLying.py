import random
from typing import Dict, List

import discord
from discord import ButtonStyle, Interaction, Member, app_commands, ui

from ..tools import Cog

RANDOM_ARTICLES = ["The Statue Of Liberty", "The Eifle Tower", "Bass Pro Shop Pyramid", "The Taj Mahal", "Fortnite"]


class ArticalModal(ui.Modal, title="My Article Is..."):
    article = ui.TextInput(label="Article Name", placeholder=random.choice(RANDOM_ARTICLES))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


class FinishView(ui.View):
    def __init__(self, articleOwner: Member, tomId):
        super().__init__(timeout=840)
        self.tomId = tomId
        self.articleOwner: Member = articleOwner

    @ui.button(label="the answer was...")
    async def answer(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message(
            f"the article was chosen by {self.articleOwner.display_name}", ephemeral=interaction.user.id != self.tomId
        )
        if interaction.user.id == self.tomId:
            self.stop()


class nOfThesePeopleAreLying(Cog):
    class ImPlaying(ui.View):
        def __init__(self, *, timeout=180):
            super().__init__(timeout=timeout)
            self.players: List[Interaction] = []
            self.orig = None

        @ui.button(label="I'm playing!")
        async def playerConfirm(self, interaction: Interaction, button: ui.Button):
            if interaction.user.id in [p.user.id for p in self.players]:
                return await interaction.response.send_message("you've already joined!", ephemeral=True)
            self.players.append(interaction)
            await interaction.response.send_message("i got you!", ephemeral=True)
            if len(self.players) == 3:
                self.startGame.disabled = False
            await self.orig(
                content=f"are you playing? hit 'I'm Playing'! I've Got {len(self.players)} players so far!", view=self
            )

        @ui.button(label="Let's Play!", style=ButtonStyle.green, disabled=True)
        async def startGame(self, interaction: Interaction, button: ui.Button):
            await interaction.response.defer(ephemeral=True)
            self.stop()

    class Articles(ui.View):
        def __init__(self, players: List[Interaction], tomId):
            super().__init__(timeout=None)
            self.articles: Dict[int, str] = dict()
            self.players = players
            self.player_ids = [p.user.id for p in self.players]
            self.tomId = tomId
            self.add_item(
                ui.Button(label="Random Wikipedia Article", url="https://en.wikipedia.org/wiki/Special:Random")
            )

        @ui.button(label="My Articles is...", style=ButtonStyle.green)
        async def articlesSet(self, interaction: discord.Interaction, button: ui.Button):
            m = ArticalModal()
            if interaction.user.id not in self.player_ids:
                return await interaction.response.send_message("You're not playing!", ephemeral=True)
            if interaction.user.id == self.tomId:
                return await interaction.response.send_message(
                    "You are playing as Tom, and don't pick an article.", ephemeral=True
                )
            if interaction.user.id in self.articles:
                return await interaction.response.send_message("You arleady responded!", ephemeral=True)
            await interaction.response.send_modal(m)
            if not await m.wait():  # this is dum
                self.articles[interaction.user.id] = m.article.value
            if len(self.players) == len(self.articles):
                self.stop()

    @app_commands.guilds(discord.Object(791528974442299412))
    @app_commands.command(name="n-of-these-people-are-lying")
    async def nLyers(self, interaction: Interaction):
        v = self.ImPlaying(timeout=None)
        v.orig = interaction.edit_original_message
        await interaction.response.send_message("are you playing? hit 'I'm Playing'! ", view=v)
        await v.wait()
        players = v.players
        tom = players.pop(random.randrange(len(players)))

        articles = self.Articles(players, tom.user.id)
        await interaction.followup.send(
            f"alright! i need {', '.join([f'**{player.user.display_name}**' for player in players])} to each go to wikipedia and grab a random article, then let me know the name of it. {tom.user.display_name} will be guessing who's got the article once all of you submit it.\n\nRemember, you don't have to pick the first article you get on the Random button.",
            view=articles,
        )

        await articles.wait()

        uid, article = random.choice(list(articles.articles.items()))
        finish = FinishView(interaction.guild.get_member(uid), tom.user.id)
        await tom.followup.send(
            f"We're {interaction.guild.name} and this is {len(v.players) - 1} of these people are lying because {len(v.players) - 1} of them will be. Currently the rest of the voice call is finding an article; after they have found an article and submitted it's name to Alexbot it Will randomly select one of the names. After the title has been selected one of the people will be telling the truth and the rest will be lying. It is your job to correctly guess who is telling the truth. If you guess who wrong, the person who deceive you will get the point.",
            ephemeral=True,
        )
        await interaction.followup.send(f"Alright, out of everyone's Articles, we got... {article}!", view=finish)


async def setup(bot):
    await bot.add_cog(nOfThesePeopleAreLying(bot))
