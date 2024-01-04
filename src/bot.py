import requests 
import os
import asyncio 
import time
import random as rd
import pickle
from datetime import datetime

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
            body.append([entrant['rank'], entrant['user_info']['name'], entrant['user_info']['Konami_id']])

        table = table2ascii(header=header,body=body)

        message = f'```Results for tournament at {venue} on {date}\n{table}\n```[Link to Picture of Standing Used to Generate Table](<{first_attachment["url"]}>)'
    else:
        message = 'jajaja'

    await interaction.response.send_message(message)
    # await interaction.response.send_message(f'```Results for tournament at {venue} on {date}\n{table}\n```[Link to Standing](<{first_attachment["url"]}>)')

    #[Picture of Standings]({first_attachment["url"]})

    # await interaction.response.send_message(f"{first_attachment['url']} \n added the following Date:{None} Venue:{None}")

@client.tree.command(name='get_users_results')
async def get_users_results(interaction:discord.Interaction, konami_id:int=None,user:str=None):
    print(user)

@client.tree.command(name='get_tournament_results')
async def get_users_results(interaction:discord.Interaction, location:str=None,date:str=None):
    pass
    

client.run(os.getenv('Disc_Token'))
