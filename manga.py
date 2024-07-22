import os
from dotenv import load_dotenv
import requests

load_dotenv()

base_url = "https://api.mangadex.org"


class Chapter:
    def __init__(self, id: str, _base_url=base_url):
        self.id = id
        self.base_url = _base_url
        self.data = None

        self.update_data()

    def update_data(self):
        r = requests.get(
            f"{self.base_url}/chapter/{self.id}"
        )
        self.data = r.json()["data"]

    def get_chapter_num(self) -> str:
        return self.data["attributes"]["chapter"]

    def get_chapter_url(self) -> str:
        return self.data["attributes"]["readableAt"]

    def __str__(self):
        return str({
            "chapter_num": self.get_chapter_num(),
        })


class Manga:
    def __init__(self, id: str, _base_url=base_url):
        self.id = id
        self.base_url = _base_url
        self.data = None

        self.update_data()

    def update_data(self):
        r = requests.get(
            f"{self.base_url}/manga/{self.id}"
        )
        self.data = r.json()["data"]

    def get_title(self) -> str:
        return self.data["attributes"]["title"]

    def get_latest_chap(self) -> Chapter:
        return Chapter(self.data["attributes"]["latestUploadedChapter"])

    def get_cover_art_url(self):
        cover_art_id = ""
        for relation in self.data["relationships"]:
            if relation["type"] == "cover_art":
                cover_art_id = relation["id"]



        r = requests.get(f"{self.base_url}/cover/{cover_art_id}")
        print( r.json()["data"])
        cover_id = r.json()["data"]["attributes"]["fileName"]
        return f"https://mangadex.org/covers/{self.id}/{cover_id}"

    def get_description(self) -> str:
        if "en" in self.data["attributes"]["description"].keys():
            return self.data["attributes"]["description"]["en"]
        else:
            return self.data["attributes"]["description"][self.data["attributes"]["description"].keys()[0]]

    def get_url(self) -> str:
        return f"https://mangadex.org/title/{self.id}"

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



if __name__ == "__main__":
    mh = MangaHandler()
    print(mh.search("Release That Witch")[0].get_url())
