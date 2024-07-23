import os
import discord
from discord import app_commands

from dotenv import load_dotenv

import embed_util
import manga

mh = manga.MangaHandler()

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
    await chanel.send(view=view, embed=embed_util.manga_embed(manga_list[0]), files=embed_util.gen_manga_files(manga_list))
    await view.wait()
    await chanel.send("Done")


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1042133536926347324))
    print("Ready!")


client.run(os.environ.get("BOT_TOKEN"))
