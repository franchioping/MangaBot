import os
from dotenv import load_dotenv
import requests

load_dotenv()

base_url = "https://api.mangadex.org"


class Chapter:
    def __init__(self, id: str, _base_url=base_url):
        self.id = id
        self.base_url = _base_url

    def _get_self(self):
        r = requests.get(
            f"{self.base_url}/chapter/{self.id}"
        )
        return r.json()["data"]

    def get_chapter_num(self) -> str:
        return self._get_self()["attributes"]["chapter"]

    def get_chapter_url(self) -> str:
        return self._get_self()["attributes"]["readableAt"]

    def __str__(self):
        return str({
            "chapter_num": self.get_chapter_num(),
        })


class Manga:
    def __init__(self, id: str, _base_url=base_url):
        self.id = id
        self.base_url = _base_url

    def _get_self(self):
        r = requests.get(
            f"{self.base_url}/manga/{self.id}"
        )
        return r.json()["data"]

    def get_title(self) -> str:
        return self._get_self()["attributes"]["title"]

    def get_latest_chap(self) -> Chapter:
        return Chapter(self._get_self()["attributes"]["latestUploadedChapter"])

    def __str__(self):
        return str({
            "title": self.get_title(),
            "latest_chapter": str(self.get_latest_chap())
        })


class MangaHandler:
    def __init__(self):
        self.base_url = base_url

    def search(self, title: str) -> list[Manga]:
        r = requests.get(
            f"{self.base_url}/manga",
            params={"title": title}
        )
        data = r.json()["data"]
        manga_list: list[Manga] = []
        for manga in data:
            manga_id = manga["id"]
            manga_list.append(Manga(manga_id))

        return manga_list

    def get_chapter(self, chapter_id: str):
        r = requests.get(
            f"{self.base_url}/chapter/{chapter_id}"
        )
        return r.json()["data"]


if __name__ == "__main__":
    mh = MangaHandler()
    print(mh.search("Release That Witch")[0].get_latest_chap().get_chapter_num())
