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

    def get_chapters(self, manga_to_get: md.series.Manga):
        return self.chapter.get_chapter_list(manga=manga_to_get.manga_id)


if __name__ == "__main__":
    mw = MangaWrapper()
    manga = mw.search("I Turned off the Pain Perception Setting!")[0]
    chaps = mw.get_chapters(manga)
    print(chaps)
