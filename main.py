import os
import discord
from discord import app_commands

from dotenv import load_dotenv

import embed_util
import manager
import manga_api

mh = manga_api.MangaHandler()
man = manager.Manager()

load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(
    name="ping",
    description="My first application Command",
    guild=discord.Object(id=1042133536926347324)
)
async def first_command(interaction: discord.Interaction):
    chanel = await interaction.user.create_dm()
    await chanel.send("Hi")


@tree.command(
    name="search",
    description="Search for manga to follow",
    guild=discord.Object(id=1042133536926347324)
)
@app_commands.describe(title='Title of the manga to search for')
async def search_command(
        interaction: discord.Interaction,
        title: str
):
    await interaction.response.send_message("Check your DM's")
    chanel = await interaction.user.create_dm()

    manga_list = mh.search(title)
    view = embed_util.ListManga(manga_list)
    await chanel.send(f"Hey, you searched for {title}")
    msg = await chanel.send(view=view, embed=embed_util.manga_embed(manga_list[0]))
    await view.force_reload(msg)
    await view.wait()

    ret: list[dict] = view.ret
    for action in ret:
        if action["action"] == 1:
            manga_id = action["manga"]
            man.add_user_to_manga(interaction.user, manga_api.Manga(manga_id))
        if action["action"] == -1:
            manga_id = action["manga"]
            man.remove_user_from_manga(interaction.user, manga_api.Manga(manga_id))


    await chanel.send("Done")
    await man.update()


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1042133536926347324))
    print("Ready!")


client.run(os.environ.get("BOT_TOKEN"))
