import os
import discord
from discord import app_commands
from discord.ext import tasks

from dotenv import load_dotenv

import embed_util
import manager
import manga_api

mh = manga_api.MangaHandler()

load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

man = manager.Manager(client)


@tree.command(
    name="ping",
    description="My first application Command",
    guild=discord.Object(id=1042133536926347324)
)
async def first_command(interaction: discord.Interaction):
    chanel = await interaction.user.create_dm()
    await chanel.send("Hi")


async def render_manga_list_in_dm(interaction: discord.Interaction, manga_list: list[manga_api.Manga]):
    chanel = await interaction.user.create_dm()

    if len(manga_list) == 0:
        await chanel.send("No Manga in Here")
        return

    view = embed_util.ListManga(manga_list)
    msg = await chanel.send(view=view, embed=embed_util.manga_embed(manga_list[0]))
    view.set_msg(msg)
    await view.force_reload()

    await interaction.followup.send("Query done, Check your DM's")

    await view.wait()

    print("Done.. Checking Returns")
    ret: list[dict] = view.ret
    for action in ret:
        if action["action"] == 1:
            manga_id = action["manga"]
            print(f"Userid {interaction.user.id} added mangaid {manga_id}")
            man.add_user_to_manga(interaction.user, manga_api.Manga(manga_id))
        if action["action"] == -1:
            manga_id = action["manga"]
            print(f"Userid {interaction.user.id} removed mangaid {manga_id}")
            man.remove_user_from_manga(interaction.user, manga_api.Manga(manga_id))

    await msg.delete()
    await man.update()


@tree.command(
    name="search",
    description="Search for manga to follow",
)
@app_commands.describe(title='Title of the manga to search for')
async def search_command(
        interaction: discord.Interaction,
        title: str
):
    await interaction.response.defer()

    await render_manga_list_in_dm(interaction, mh.search(title))


@tree.command(
    name="list",
    description="List the manga you follow",
)
async def list_command(interaction: discord.Interaction):
    await interaction.response.defer()

    await render_manga_list_in_dm(interaction, man.get_user_mangas(interaction.user))


@tasks.loop(minutes=5)
async def update_manga():
    print("Updating... ")
    await man.update()
    print("Update Finished!")


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1042133536926347324))
    await tree.sync()
    print("Ready!")


client.run(os.environ.get("BOT_TOKEN"))
