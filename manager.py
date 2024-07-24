import discord
import json

import embed_util
import manga_api

_manager = None


class Manager:
    def __init__(self, client):
        self.client: discord.Client = client
        self.manga = {}
        self.chapters = {}

    def add_user_to_manga(self, user: discord.User, manga: manga_api.Manga) -> None:
        if manga.id in self.manga.keys():
            self.manga[manga.id].append(user.id)
        else:
            self.manga[manga.id] = [user.id]

    def remove_user_from_manga(self, user: discord.User, manga: manga_api.Manga) -> None:
        if manga.id in self.manga.keys():
            self.manga[manga.id].remove(user.id)
        else:
            self.manga[manga.id] = []

    async def update(self):
        for manga_id in self.manga.keys():
            manga = manga_api.Manga(manga_id)
            new_chap = self.check_for_new_chapter(manga)
            if new_chap is not None:
                users = self.manga[manga_id]
                print(users)
                for userid in users:
                    await self.send_message_to_user(await self.client.fetch_user(userid), manga, new_chap)
        self.save()

    def check_for_new_chapter(self, manga: manga_api.Manga) -> manga_api.Chapter | None:
        latest_chap = manga.get_latest_chap()
        if latest_chap not in self.chapters.keys():
            self.chapters[manga.id] = latest_chap.id
            return latest_chap
        if latest_chap.is_more_recent_than(manga_api.Chapter(self.chapters[manga.id])):
            self.chapters[manga.id] = latest_chap.id
            return latest_chap
        else:
            return None

    async def send_message_to_user(self, user: discord.User, manga: manga_api.Manga,
                                   chapter: manga_api.Chapter) -> None:
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=embed_util.chapter_embed(manga, chapter), files=embed_util.get_chapter_files(manga))

    def save(self):
        with open("manager.json", "w") as f:
            json.dump(self.to_dict(), f)

    def to_dict(self):
        return {
            "manga": self.manga,
            "chapters": self.chapters
        }
