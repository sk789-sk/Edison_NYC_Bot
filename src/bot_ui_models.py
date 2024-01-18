import discord
from discord.ext import commands
# from discord.ext.commands import Converter, BadArgument


class dropdown(discord.ui.Select):
    def __init__(self,options=[discord.SelectOption(label='placeholder')],placeholder='Select a Tournament from Dropdown'):
        super().__init__(placeholder=placeholder, options=options, min_values=1, max_values=1)

    async def callback(self, interaction):
        return self.values


class dropdownView(discord.ui.View):
    def __init__(self, options=None, placeholder=None, timeout=60.0):
        super().__init__(timeout=timeout)
        self.add_item(dropdown(options=options, placeholder=placeholder))

    
class NameConverter(commands.Converter):
    async def convert(self, ctx, argument:str): 
        if len(argument) <2:
            raise commands.BadArgument("At Least 2 characters needed for Search")
        return argument
    
        return await super().convert(ctx, argument)