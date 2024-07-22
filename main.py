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
)
async def first_command(interaction: discord.Interaction):
    chanel = await interaction.user.create_dm()
    await chanel.send("Hi")


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
