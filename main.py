import os
import discord
from discord import app_commands
from discord.ext import tasks

from dotenv import load_dotenv

import embed_util
import manager
import manga_api
from util import parallel_downloads

mh = manga_api.MangaHandler()

load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

man = manager.Manager(client)


async def render_manga_list_in_dm(interaction: discord.Interaction, manga_list: list[manga_api.Manga]):
    chanel = await interaction.user.create_dm()
    await interaction.followup.send("Check your DM's")

    if len(manga_list) == 0:
        await chanel.send("No Manga in Here")
        return

    list_msg = await chanel.send(embed=embed_util.manga_list_embed(manga_list))
    view = embed_util.ListManga(manga_list, await man.get_user_mangas(interaction.user))
    msg = await chanel.send(view=view, embed=await embed_util.manga_embed(manga_list, 0),
                            files=[parallel_downloads.discord_file_from_filename(filename) for filename in
                                   embed_util.get_chapter_filenames(manga_list[0])]
                            )

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
    await list_msg.delete()
    await man.update()


@tree.command(
    name="search",
    description="Search for manga to follow",
)
@app_commands.describe(title='Title of the manga to search for')
@app_commands.user_install()
@discord.app_commands.guild_install()
async def search_command(
        interaction: discord.Interaction,
        title: str
):
    await interaction.response.defer()

    await render_manga_list_in_dm(interaction, await mh.search(title))


@tree.command(
    name="list",
    description="List the manga you follow",
)
@app_commands.user_install()
@discord.app_commands.guild_install()
async def list_command(interaction: discord.Interaction):
    await interaction.response.defer()

    await render_manga_list_in_dm(interaction, await man.get_user_mangas(interaction.user))


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
