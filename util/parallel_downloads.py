import concurrent.futures
import requests
import os.path


import discord
from manga_api import Manga


def download_file(manga: Manga):
    extension = manga.get_cover_art_extension()
    if not os.path.isfile(f'tmp/{manga.id}.{extension}'):
        img_data = requests.get(manga.get_cover_art_url()).content
        with open(f'tmp/{manga.id}.{extension}', 'wb') as handler:
            handler.write(img_data)
    return discord.File(f"tmp/{manga.id}.{extension}", f"{manga.id}.{extension}")

def parallel_download(manga_list: list[Manga]) -> list[discord.File]:
    with concurrent.futures.ThreadPoolExecutor() as exector:
        result = exector.map(download_file, manga_list)

    return list(result)

