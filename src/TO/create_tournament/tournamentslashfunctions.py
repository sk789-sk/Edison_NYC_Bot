import requests
import asyncio
import discord
from discord.ext import commands

from bot_ui_models import dropdownView


baseURL = 'http://127.0.0.1:5556/'

async def create_slash(interaction:discord.Interaction,client:commands.Bot,name,game):
    
    formats = ['Swiss', 'Round Robin', 'Single Elim', 'Double Elim']

    dropdown_vals = [discord.SelectOption(label=format, value=format) for format in formats]

    await interaction.response.send_message("",view=dropdownView(options=dropdown_vals),ephemeral=True)

    response = 'Test'
    await interaction.response.send_message(response)


async def join_slash():
    pass

async def start_slash():
    pass

async def loss_slash():
    pass

async def start_next_round_slash():
    pass

async def end_slash():
    pass

async def standings_slash():
    pass

async def drop_slash():
    pass