import concurrent.futures
import requests
import os.path


import discord
from manga_api import Manga

DOWNLOAD_DIRECTORY = 'tmp/'


def discord_file_from_filename(filename: str) -> discord.File:
    return discord.File(f"{DOWNLOAD_DIRECTORY}{filename}",filename)
def download_file(manga: Manga) -> str:
    extension = manga.get_cover_art_extension()
    if not os.path.isfile(f'{DOWNLOAD_DIRECTORY}/{manga.id}.{extension}'):
        img_data = requests.get(manga.get_cover_art_url()).content
        with open(f'{DOWNLOAD_DIRECTORY}/{manga.id}.{extension}', 'wb') as handler:
            handler.write(img_data)
    return f"{manga.id}.{extension}"

def parallel_download(manga_list: list[Manga]) -> list[str]:
    print("Downloading Images...")
    with concurrent.futures.ThreadPoolExecutor() as exector:
        result = exector.map(download_file, manga_list)
    print("Images Finished Downloading")
    return list(result)

