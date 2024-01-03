import requests 
import os
import asyncio 
import time
import random as rd
import pickle

import discord 
from discord.ext import commands
from dotenv import load_dotenv

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

@client.tree.command(name='upload_standings', description='upload image of final standing')
async def upload_img_slash(interaction:discord.Interaction, image:discord.Attachment):

    #upload the processed image to the OCR API or do it on my pc idk
    #Check parsed information for errors. 
    #Put relevant information into the database

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

        print(response.json().keys())
        
        text = data['ParsedResults'][0]['ParsedText']

        

            
        print(text)


    with open('test.pkl','wb') as f:
        pickle.dump(text,f)


    await interaction.response.send_message(f"{first_attachment['url']} ")



client.run(os.getenv('Disc_Token'))
