import discord
import json

import embed_util
import manga_api

import os.path
from util import parallel_downloads


class Manager:
    def __init__(self, client, savefile: str = "manager.json"):
        self.client: discord.Client = client
        self.manga = {}
        self.chapters = {}
        self.savefile = savefile

        self.load()

    async def get_user_mangas(self, user: discord.User) -> list[manga_api.Manga]:
        manga_ids = []

        for manga_id in self.manga.keys():
            if user.id in self.manga[manga_id]:
                manga_ids.append(manga_id)

        return [await manga_api.Manga.init(manga_id) for manga_id in manga_ids]

    def add_user_to_manga(self, user: discord.User, manga: manga_api.Manga) -> None:
        if manga.id in self.manga.keys():
            self.manga[manga.id].append(user.id)
        else:
            self.manga[manga.id] = [user.id]

    def remove_user_from_manga(self, user: discord.User, manga: manga_api.Manga) -> None:
        if manga.id in self.manga.keys():
            if user.id in self.manga[manga.id]:
                self.manga[manga.id].remove(user.id)
                if len(self.manga[manga.id]) == 0:
                    self.manga.pop(manga.id)
        else:
            self.manga[manga.id] = []

    async def update(self):
        for manga_id in self.manga.keys():
            manga = await manga_api.Manga.init(manga_id)
            new_chap = await self.check_for_new_chapter(manga)
            if new_chap is not None:
                users = self.manga[manga_id]
                print(users)
                for userid in users:
                    await self.send_message_to_user(await self.client.fetch_user(userid), manga, new_chap)
        self.save()

    async def check_for_new_chapter(self, manga: manga_api.Manga) -> manga_api.Chapter | None:
        latest_chap = await manga.get_latest_chap()
        print("Comparing Chapters...")

        if manga.id not in self.chapters.keys():
            self.chapters[manga.id] = latest_chap.id
            return latest_chap
        old_chap = await manga_api.Chapter.init(self.chapters[manga.id])

        print(f"Latest Chap ID: {latest_chap.id}, Old Chap ID: {self.chapters[manga.id]}")
        print(f"Latest Chap: {latest_chap.get_volume()}:{latest_chap.get_number()}")
        print(f"Latest Chap: {old_chap.get_volume()}:{old_chap.get_number()}")
        if latest_chap.is_more_recent_than(old_chap):
            self.chapters[manga.id] = latest_chap.id
            print("New Latest Chap!")
            return latest_chap
        else:
            print("No New Chapter.")
            return None

    async def send_message_to_user(self, user: discord.User, manga: manga_api.Manga,
                                   chapter: manga_api.Chapter) -> None:
        dm_channel = await user.create_dm()
        await dm_channel.send(
            embed=await embed_util.chapter_embed(manga, chapter),
            files=[parallel_downloads.discord_file_from_filename(filename) for filename in
                   embed_util.get_chapter_filenames(manga)]
        )

    def save(self):
        with open(self.savefile, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def load(self):
        if os.path.isfile(self.savefile):
            with open(self.savefile, "r") as f:
                self.from_dict(json.load(f))

    def from_dict(self, data: dict):
        self.manga = data["manga"]
        self.chapters = data["chapters"]

    def to_dict(self):
        return {
            "manga": self.manga,
            "chapters": self.chapters
        }
