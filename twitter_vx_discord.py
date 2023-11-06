import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
TOKEN = 'MTE3MDg5NzQ2MzgxNzc5NzY5Mw.GjbIXD.XkWt3D3dKhA_YUZnOm4kcbiWpXKsKeDGtiusdo'
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
        if guild.name == GUILD:
            break

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
        
        if 'x.' in message.content:
            modified_message = content.replace('x.com', 'vxtwitter.com')
        else:
            modified_message = content.replace('twitter.com', 'vxtwitter.com')

        if message.author != bot.user:
            # Check if the message author is not the bot
            await message.delete()  # Delete the user's message
             # Send the modified URL as a new message
            await message.channel.send(f":index_pointing_at_the_viewer: TWEET :index_pointing_at_the_viewer: from **{message.author.name}** : {modified_message}")


        print("did it change?")
    
    await bot.process_commands(message)  # Process commands as well

def is_twitter_url(content):
   # print("Content:",content)
    print(re.search(r'https?://(?:www\.)?twitter\.com/\S+/status/\d+', content))
    return re.search(r'https?://(?:www\.)?twitter\.com/\S+/status/\d+', content) or (r'https?://(?:www\.)?x\.com/\S+/status/\d+', content) 

bot.run(TOKEN)
