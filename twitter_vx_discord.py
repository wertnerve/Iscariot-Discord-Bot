#!/usr/bin/env python
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import re

#This script runs the backend of the Jahnel Discord Bot.
#It will check for any messages with a twitter.com or x.com URL and replace it with vxtwitter.com.
#This restores embedded functionality
load_dotenv()
#TOKEN = os.getenv('DISCORD_TOKEN')
#GUILD = os.getenv('DISCORD_GUILD')
print('Starting up Jahnel Bot')
TOKEN = 'MTE3MDg5NzQ2MzgxNzc5NzY5Mw.G31Bra.8wU8OPxXSVpkFm5dDJNZoTj0E1lMMTIaOyDrDQ'
print(TOKEN)

# Define your bot's intents
intents = discord.Intents.all()
intents.typing = False
intents.presences = False

# Regular expression pattern to match a Twitter URL
twitter_url_pattern = r'https?://(?:www\.)?twitter\.com/\S+/status/\d+'

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    for guild in bot.guilds:


         print(
        f'{bot.user} is connected to the following serverss:\n'
        f'{guild.name}(id: {guild.id})'
        )

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Skip messages sent by the bot itself

    content = message.clean_content

    if is_twitter_url(message.content):

        if re.search(r'https?://(?:www\.)?x\.com/\S+/status/\d+',message.content): #x.com
            modified_message = content.replace('x.com', 'vxtwitter.com')

        else:
            modified_message = content.replace('twitter.com', 'vxtwitter.com')

        if message.author != bot.user:
            # Check if the message author is not the bot
            await message.delete()  # Delete the user's message
             # Send the modified URL as a new message
            await message.channel.send(f":index_pointing_at_the_viewer: TWEET :index_pointing_at_the_viewer: from **{message.author.name}** : {modified_message}")




    await bot.process_commands(message)  # Process commands as well

def is_twitter_url(content):
   # print("Content:",content)
#    print(re.search(r'https?://(?:www\.)?twitter\.com/\S+/status/\d+', content))
    return re.search(r'https?://(?:www\.)?twitter\.com/\S+/status/\d+', content) or re.search(r'https?://(?:www\.)?x\.com/\S+/status/\d+', content)

bot.run(TOKEN)
