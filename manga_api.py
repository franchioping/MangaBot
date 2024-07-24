import os
from dotenv import load_dotenv
import requests
import asyncio


load_dotenv()

base_url = "https://api.mangadex.org"


class Chapter:
    def __init__(self, id: str, _base_url=base_url):
        self.id = id
        self.base_url = _base_url
        self.data = None

        self.update_data()

    @classmethod
    async def init(cls, id: str , _base_url=base_url):
        self = cls(id, _base_url)
        await self.update_data()
        return self

    async def update_data(self):
        r = requests.get(
            f"{self.base_url}/chapter/{self.id}"
        )
        self.data = r.json()["data"]

    def is_more_recent_than(self, chapter):
        if chapter.get_volume() != self.get_volume():
            return float(self.get_volume()) > float(chapter.get_volume())
        return float(self.get_number()) > float(chapter.get_number())

    def get_title(self) -> str | None:
        return self.data["attributes"]["title"] if self.data["attributes"]["title"] else None

    def get_volume(self) -> str:
        return self.data["attributes"]["volume"]

    def get_number(self) -> str:
        return self.data["attributes"]["chapter"]

    def get_url(self) -> str:
        return f"https://mangadex.org/chapter/{self.id}"

    def __str__(self):
        return str({
            "id": self.id,
            "chapter_vol": self.get_volume(),
            "chapter_num": self.get_number(),
            "chapter_url": self.get_url()
        })

    def __eq__(self, other):
        return self.id == other.id


class Manga:
    def __init__(self, id: str, _base_url=base_url):
        self.id = id
        self.base_url = _base_url
        self.data = None

    @classmethod
    async def init(cls, id: str, _base_url=base_url):
        self = cls(id, _base_url)
        await self.update_data()
        return self


    async def update_data(self):
        r = requests.get(
            f"{self.base_url}/manga/{self.id}"
        )
        self.data = r.json()["data"]

    def get_title(self) -> str:
        try:
            return self.data["attributes"]["title"]["en"]
        except KeyError:
            try:
                return self.data["attributes"]["title"][0]
            except KeyError:
                return "No Title"

    async def get_latest_chap(self) -> Chapter:
        params = {
            "manga": self.id,
            "translatedLanguage": ["en"],
            "order": {
                "chapter": "desc"
            }
        }
        r = requests.get(
            f"{self.base_url}/chapter?manga={self.id}&originalLanguage%5B%5D=en&contentRating%5B%5D=safe"
            f"&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&includeFutureUpdates=1&order%5Bchapter%5D"
            f"=desc",

        )
        if r.json()["total"] == 0:
            r = requests.get(
                f"{self.base_url}/chapter?manga={self.id}&translatedLanguage%5B%5D=en&contentRating%5B%5D=safe"
                f"&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&includeFutureUpdates=1&order%5Bchapter"
                f"%5D=desc",
            )

        latest_chap = r.json()["data"][0]

        return Chapter(latest_chap["id"])

    def get_cover_art_url(self):
        cover_art_id = ""
        for relation in self.data["relationships"]:
            if relation["type"] == "cover_art":
                cover_art_id = relation["id"]

        r = requests.get(f"{self.base_url}/cover/{cover_art_id}")
        cover_fileName = r.json()["data"]["attributes"]["fileName"]
        cover_extension = cover_fileName.split(".")[1]
        return f"https://mangadex.org/covers/{self.id}/{cover_fileName}.256.{cover_extension}"

    def get_cover_art_extension(self):
        cover_art_id = ""
        for relation in self.data["relationships"]:
            if relation["type"] == "cover_art":
                cover_art_id = relation["id"]

        r = requests.get(f"{self.base_url}/cover/{cover_art_id}")
        cover_fileName = r.json()["data"]["attributes"]["fileName"]
        cover_extension = cover_fileName.split(".")[1]
        return cover_extension

    def get_description(self) -> str:
        if "en" in self.data["attributes"]["description"].keys():
            return self.data["attributes"]["description"]["en"]
        else:
            if len(list(self.data["attributes"]["description"].keys())) > 0:
                return self.data["attributes"]["description"][list(self.data["attributes"]["description"].keys())[0]]
            return ""

    def get_url(self) -> str:
        return f"https://mangadex.org/title/{self.id}"

    def __str__(self):
        return str({
            "id": self.id,
            "title": self.get_title(),
            "url": self.get_url(),
            "art_url": self.get_cover_art_url(),
            "latest_chapter": str(asyncio.ensure_future(self.get_latest_chap()))
        })

    def __eq__(self, other):
        return self.id == other.id


class MangaHandler:
    def __init__(self):
        self.base_url = base_url

    async def search(self, title: str) -> list[Manga]:
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


if __name__ == "__main__":
    mh = MangaHandler()