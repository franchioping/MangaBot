import os
import discord
from discord import app_commands

from dotenv import load_dotenv

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
async def first_command(
        interaction: discord.Interaction,
        title: str
):
    await interaction.response.send_message("Check your DM's")
    chanel = await interaction.user.create_dm()
    await chanel.send(f"Hey, you searched for {title}")


@client.event
async def on_message(message: discord.Message):
    if isinstance(message.channel, discord.DMChannel):
        user = message.author
        channel = message.channel


    

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1042133536926347324))
    print("Ready!")


client.run(os.environ.get("BOT_TOKEN"))
