import mangadex as md
import os
from dotenv import load_dotenv

load_dotenv()


class MangaWrapper:
    def __init__(self):
        self.auth = md.auth.Auth()
        self.auth.login(os.environ.get("MANGADEX_USR"),
                        os.environ.get("MANGADEX_PSWD"),
                        os.environ.get("MANGADEX_CLIENT"),
                        os.environ.get("MANGADEX_TOKEN")
                        )
        self.manga = md.series.Manga(auth=self.auth)
        self.chapter = md.series.Chapter(auth=self.auth)

    def search(self, title: str, limit: int = 10) -> list[md.series.Manga]:
        return self.manga.get_manga_list(title=title)

    def get_latest_chapter(self, manga_to_get: md.series.Manga) -> int:
        manga_feed = self.manga.manga_feed(manga_id=manga_to_get.manga_id)
        print(manga_feed[0].chapter)




if __name__ == "__main__":
    mw = MangaWrapper()
    manga = mw.search("Release That Witch")[0]
    print(manga.title)
    mw.get_latest_chapter(manga)
