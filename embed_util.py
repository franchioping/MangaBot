from manga_api import Manga, Chapter
import discord
import os.path

import requests
from util import parallel_downloads


class ListManga(discord.ui.View):
    def __init__(self, manga_list: list[Manga]):
        super().__init__()
        self.ret = []
        self.index = 0
        self.manga_list = manga_list
        self.manga_files = gen_manga_files(self.manga_list)

    async def force_reload(self, msg: discord.Message):
        await msg.edit(
            embed=manga_embed(self.manga_list[self.index]),
            attachments=[self.manga_files[self.index]]
        )

    async def print_manga(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.message.edit(
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
        if self.index < len(self.manga_list) - 1:
            self.index += 1

        await self.print_manga(interaction)

    @discord.ui.button(label='Add', style=discord.ButtonStyle.green)
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.ret.append({"manga": self.manga_list[self.index].id, "action": 1})

    @discord.ui.button(label='Remove', style=discord.ButtonStyle.red)
    async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.ret.append({"manga": self.manga_list[self.index].id, "action": -1})

    @discord.ui.button(label='Done', style=discord.ButtonStyle.blurple)
    async def exit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.ret) > 0:
            await interaction.response.send_message("Your list has been altered successfully", ephemeral=True)
        else:
            await interaction.response.send_message("You didn't make any changes", ephemeral=True)
        self.stop()


def gen_manga_files(manga_list: list[Manga]):
    return parallel_downloads.parallel_download(manga_list)


def manga_embed(manga: Manga):
    e = discord.Embed(title=manga.get_title(), description=manga.get_description(), url=manga.get_url())
    extension = manga.get_cover_art_extension()
    e.set_thumbnail(url=f"attachment://{manga.id}.{extension}")

    return e


def get_chapter_files(manga: Manga):
    return parallel_downloads.parallel_download([manga])


def chapter_embed(manga: Manga, chapter: Chapter):
    volume_info = f"Volume {chapter.get_volume()}" if chapter.get_volume() else ""
    chapter_title = f"{chapter.get_title()}" if chapter.get_title() else ""
    e = discord.Embed(
        title=f'"{manga.get_title()}" Chapter {chapter_title} Released!',
        description=f"{volume_info} Chapter {chapter.get_number()} of {manga.get_title()} Released."
                    f"\nGo read it now!",
        url=chapter.get_url()
    )
    e.set_thumbnail(url=f"attachment://{manga.id}.{manga.get_cover_art_extension()}")
    return e
