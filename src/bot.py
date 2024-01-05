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

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True 

client = commands.Bot(command_prefix='$',intents=intents ,case_insensitive=True)

@client.event
async def on_ready():
    print(f'Logged in with {client.user}')

    try:
        synched = await client.tree.sync()
        print(f"synched with {len(synched)} commands")
    except Exception as e:
        print(e)

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
        text = data['ParsedResults'][0]['ParsedText']

    with open(f'ocr_data.pkl','wb') as f:
        pickle.dump(text,f)

    #Parse the text
        
    standing_list = parse_file('ocr_data.pkl')
    
    #Take the information and pass it to my db 

    data = {
        'date':date,
        'venue' : venue,
        'url' : first_attachment['url'],
        'entrants' : standing_list
        
    }

    r = requests.post('http://127.0.0.1:5557/addTournament', json=data, timeout=30.0)

    if r.ok:
        data = r.json()
        #Show the entrant
        header = ['Rank', 'Name', 'Konami ID']
        body = []

        for entrant in data:
            body.append([entrant['rank'], entrant['user_info']['name'], entrant['user_info']['konami_id']])

        table = table2ascii(header=header,body=body)

        message = f'```Results for tournament at {venue} on {date}\n{table}\n```[Link to Picture of Standing Used to Generate Table](<{first_attachment["url"]}>)'
    else:
        message = 'jajaja'

    await interaction.response.send_message(message)
    # await interaction.response.send_message(f'```Results for tournament at {venue} on {date}\n{table}\n```[Link to Standing](<{first_attachment["url"]}>)')

    #[Picture of Standings]({first_attachment["url"]})

    # await interaction.response.send_message(f"{first_attachment['url']} \n added the following Date:{None} Venue:{None}")

@client.tree.command(name='get_users_results', description='prioritizes user>konami_id>user_who put command')
async def get_users_results(interaction:discord.Interaction, konami_id:int=None,user:str=None):

    params = {}

    if user:
        params['discord_id'] = user[2:-1]
    elif konami_id:
        params['konami_id'] = konami_id
    else:
        params['discord_id'] = interaction.user.id
    
    query_string = urlencode(params)
    base_url = 'http://127.0.0.1:5557/userResults'

    r = requests.get(f'{base_url}?{query_string}', timeout=30.0)

    if r.ok:
        data = r.json()
        
        #Get the relavent information
        name = data['name']
        username = None

        if data['discord_id']:
            target = await client.fetch_user(data['discord_id'])
            username = target.name

        header = ['Place', 'Host','Date','Rounds']
        body = []

        for val in data['Entrant']:
            
            rank = val['rank']
            date = val['tournament_info']['date']
            host = val['tournament_info']['host']
            rounds = val['tournament_info']['rounds']
            
            body.append([rank,host,date,rounds])

        table = table2ascii(header=header,body=body)

        message = f'```Results for {name} (Discord username: {username if username else "Not-Registered"})\n{table}\n```'

    elif r.status_code==404:
        message = 'User Does not exist, double check Konami id and/or discord id'
    else:
        message = 'Server Error, try again'
    
    await interaction.response.send_message(message)

@client.tree.command(name='get_tournament_results',description='displays last 10 tournament from dropdown or results for specific tournament if criteria')
async def get_tournament_results(interaction:discord.Interaction, location:str=None,date:str=None):
    pass
    
@client.tree.command(name='info', description='get your konami id, and name you are registered with')
async def info(interaction:discord.Interaction):
    pass

client.run(os.getenv('Disc_Token'))
