from manga import Manga, Chapter
import discord
import os.path

import requests


class ListManga(discord.ui.View):
    def __init__(self, manga_list: list[Manga]):
        super().__init__()
        self.ret = []
        self.index = 0
        self.manga_list = manga_list
        self.manga_files = gen_manga_files(self.manga_list)
        self.msg = None

    async def print_manga(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.msg.edit(
            embed=manga_embed(self.manga_list[self.index]),
            attachments=[self.manga_files[self.index]]
        )

    @discord.ui.button(label='Prev', style=discord.ButtonStyle.grey)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index > 0:
            self.index -= 1

        await self.print_manga(interaction)

    @discord.ui.button(label='Next', style=discord.ButtonStyle.grey)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index < len(self.manga_list):
            self.index += 1

        await self.print_manga(interaction)

    @discord.ui.button(label='Add', style=discord.ButtonStyle.green)
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.ret.append({"manga": self.manga_list[self.index], "action": 1})

    @discord.ui.button(label='Remove', style=discord.ButtonStyle.red)
    async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.ret.append({"manga": self.manga_list[self.index], "action": -1})

    @discord.ui.button(label='Done', style=discord.ButtonStyle.blurple)
    async def exit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.ret) > 0:
            await interaction.response.send_message("Your list has been altered successfully", ephemeral=True)
        else:
            await interaction.response.send_message("You didn't make any changes", ephemeral=True)
        self.stop()


def gen_manga_files(manga_list: list[Manga]):
    ret = []
    for manga in manga_list:
        if not os.path.isfile(f'tmp/{manga.id}.jpg'):
            img_data = requests.get(manga.get_cover_art_url()).content
            with open(f'tmp/{manga.id}.jpg', 'wb') as handler:
                handler.write(img_data)
        ret.append(discord.File(f"tmp/{manga.id}.jpg", f"{manga.id}.jpg"))
    return ret


def manga_embed(manga: Manga):
    e = discord.Embed(title=manga.get_title(), description=manga.get_description(), url=manga.get_url())

    e.set_thumbnail(url=f"attachment://{manga.id}.jpg")

    return e
