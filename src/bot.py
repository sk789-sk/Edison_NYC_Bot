import requests 
import os
import asyncio 
import time
import random as rd
import pickle
from datetime import datetime
from urllib.parse import urlencode

import discord 
from discord.ext import commands
from dotenv import load_dotenv
from table2ascii import table2ascii

from parse_ocr import parsetext , parse_file
from bot_ui_models import dropdownView
from bot_ui_functions import create_tournament_table, create_user_table , build_query_string

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True 
intents.members = True

client = commands.Bot(command_prefix='$',intents=intents ,case_insensitive=True)

@client.event
async def on_ready():
    print(f'Logged in with {client.user}')
    try:
        synched = await client.tree.sync()
        print(f"synched with {len(synched)} commands")
    except Exception as e:
        print(e)

@client.event
async def on_member_join(member):
    print(f'{member} has joined')
    #DM the member asking for a name, can register with konami id as well
    #Take the response from the DM 
    try:
        await member.send("name pls")
        def check(m):
            return m.author == member
        try:
            response = client.wait_for('message',check=check, timeout=30.0)
            users_name = response.content
        except asyncio.TimeoutError:
            await member.send('gimme name')
    except: #idk what the error for unable to send a DM is
        print('no name')

    #Take the name and then use that to create a new user.
    #Should do some kind of moderation for bs names, or no names.
    #Maybe for no names give them only view permissions?
    #Maybe kick people after x time after joining if nothing.


@client.tree.command(name='hello')
async def hello(interaction:discord.Interaction):
    await interaction.response.send_message("hello!", ephemeral=True)

@client.tree.command(name='rps')
async def rps(interaction:discord.Interaction):
    val = rd.choice(['rock', 'paper', 'scissors'])    
    await interaction.response.send_message(val, ephemeral=True)

@client.tree.command(name='upload_standings', description='upload image of final standing \ndate format: mm-dd-year default todays date' )
async def upload_img_slash(interaction:discord.Interaction, image:discord.Attachment, venue:str, date:str=None):

    if date is None:
        date = datetime.now().strftime("%m-%d-%Y")

    print(date)

    filename = f"uploaded_image_{int(time.time())}.jpg"
    resolved_attachments = interaction.data.get('resolved').get('attachments')
    first_attachment = next(iter(resolved_attachments.values()), {})
    
    r = requests.get(first_attachment['url'], timeout=30.0)

    if r.ok:
        image = r.content

        filename = f"uploaded_image_{int(time.time())}.jpg"

        folder = 'NYC_Edison'
        os.makedirs(folder, exist_ok=True)

        file_path = os.path.join(folder,filename)

        with open(file_path, "wb") as file:
            file.write(image)
        
    #Take the Image and post it to the OCR API
    
    ocr_key = os.getenv('OCR_API_Key')
    url = "https://api.ocr.space/parse/image"

    payload = {
        'language' : 'eng',
        'isOverlayRequired' : 'false',
        'isTable' : 'True',
        'url' : first_attachment['url']
    }

    headers = {
        'apikey':ocr_key
    }

    response = requests.request("POST", url, headers=headers, data=payload, timeout=60.0)
    
    #Parsed Results -->list[0] --> Parsed Text
    #Alot of unused info probably better this way and getting error codes vs parsing entire dictionar

    if response.ok:
        data = response.json()
        
        if data['IsErroredOnProcessing'] == False:
            text = data['ParsedResults'][0]['ParsedText']
        else:
            error_message = data['ErrorMessage']
            return await interaction.response.send_message(error_message)
    else:
        return await interaction.response.send_message("Error Getting Image Data")

    with open(f'ocr_data.pkl','wb') as f:
        pickle.dump(text,f)

    #Parse the text
        
    standing_list = parse_file('ocr_data.pkl')
    

    #Take the information and pass it to my api 
    
    data = {
        'date':date,
        'venue' : venue,
        'url' : first_attachment['url'],
        'entrants' : standing_list
        
    }

    r = requests.post('http://127.0.0.1:5557/addTournament', json=data, timeout=30.0)

    if r.ok:
        data = r.json()


        #table = create_tournament_table(data)

        header = ['Rank', 'Name', 'Konami ID']
        body = []

        for entrant in data:
            body.append([entrant['rank'], entrant['user_info']['name'], entrant['user_info']['konami_id']])

        table = table2ascii(header=header,body=body)
        
        message = f'```Results for tournament at {venue} on {date}\n{table}\n```[Link to Picture of Standing Used to Generate Table](<{first_attachment["url"]}>)'
    elif r.status_code==409:
        message = 'Tournament already submitted'
    else:
        message = 'Failed to Create'

    await interaction.response.send_message(message)
    
@client.tree.command(name='get_users_results', description='prioritizes user>konami_id>name>user_who put command')
async def get_users_results(interaction:discord.Interaction, konami_id:int=None,user:str=None,name:str=None):

    params = {}

    if user:
        params['discord_id'] = user[2:-1]
    elif konami_id:
        params['konami_id'] = konami_id
    elif name:
        #strip leading leading and trailing whitespace, lower case 
        modified_name = name
        params['name'] = modified_name

    else:
        params['discord_id'] = interaction.user.id
    
    query = urlencode(params)
    base_url = 'http://127.0.0.1:5557/userResults'

    r = requests.get(f'{base_url}?{query}', timeout=30.0)

    if r.status_code==200:
        data = r.json()
        
        #Get the relavent information

        name = data['name']
        username = None

        if data['discord_id']:
            target = await client.fetch_user(data['discord_id'])
            username = target.name

        table = create_user_table(data)

        message = f'```Results for {name} (Discord username: {username if username else "Not-Registered"})\n{table}\n```'

    elif r.status_code==206: #Really just have it send back the 200 and and check for what data is and decide waht to do instead of this tbh

        #create dropdown of potential users
        data = r.json()
        options_list = [discord.SelectOption(label = f'{user["name"]}  id:{user["konami_id"]}', value = idx, description= f'') for idx,user in enumerate(data)]

        await interaction.response.send_message("Multiple potential users. Select 1 from dropdown.",view=dropdownView(options=options_list), ephemeral=True)

        try:
            interaction = await client.wait_for('interaction', timeout=30.0)
            user_idx = int(interaction.data["values"][0])
        
        except asyncio.TimeoutError:
            return await interaction.response.send_message('Timed out. Try again', ephemeral=True)        
        
        user_obj = data[user_idx]
        name = user_obj['name']
        
        username = None

        if user_obj['discord_id']:
            target = await client.fetch_user(user_obj['discord_id'])
            username = target.name        

        table = create_user_table(user_obj)

        message = f'```Results for {name} (Discord username: {username if username else "Not-Registered"})\n{table}\n```'

    elif r.status_code==404:
        message = 'User Does not exist, double check Konami id and/or discord id'
    else:
        message = 'Server Error, try again'
    
    await interaction.response.send_message(message)

@client.tree.command(name='get_tournament_results',description='displays last 10 tournament from dropdown or results for specific tournament if criteria')
async def get_tournament_results(interaction:discord.Interaction, location:str=None,date:str=None):
    
    #Get tournaments that fit the criteria

    params = {
        'host':location,
        'date':date,
        'limit':10
    }

    query_string = build_query_string(**params)
  
    base_url = 'http://127.0.0.1:5557/tournamentResults'

    r = requests.get(f'{base_url}?{query_string}', timeout=30.0)

    if r.ok:
        data = r.json()

        if len(data) ==1:
            t_obj = data[0]
            host,t_date,url = t_obj['host'], t_obj['date'],t_obj['url'] 

            table = create_tournament_table(t_obj)
            message_header = f'Results for {host} on {t_date}'
            message = f'```{message_header}\n{table}\n```[Link to Picture Used to Create Standing](<{url}>)'

        else:
            #we need to pick a tournament
            options_list = [discord.SelectOption(label = f'{tournament["host"]} on {tournament["date"]}', value = idx , description= f'') for idx ,tournament in enumerate(data)]

            await interaction.response.send_message("",view=dropdownView(options=options_list), ephemeral=True)
            try:
                interaction = await client.wait_for('interaction', timeout=30.0)
                t_idx = int(interaction.data["values"][0])
            
            except asyncio.TimeoutError:
                return await interaction.response.send_message('Timed out. Try again', ephemeral=True)
            
            t_obj = data[t_idx]

            host,t_date,url = t_obj['host'], t_obj['date'],t_obj['url']

            table  = create_tournament_table(t_obj)
            message_header = f'Results for {host} on {t_date}'
            message = f'```{message_header}\n{table}\n```[Link to Picture Used to Create Standing](<{url}>)'

    else:
        message = 'No Tournament with Specified criteria found, check date and spelling of location'
        # return await interaction.response.send_message(message)
        
    await interaction.response.send_message(message)


@client.tree.command(name='info', description='get your konami id, and name you are registered with')
async def info(interaction:discord.Interaction):

    pass



client.run(os.getenv('Disc_Token'))
