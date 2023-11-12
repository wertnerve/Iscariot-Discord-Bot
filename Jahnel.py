import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import youtube_dl
import ffmpeg
import re
from collections import deque
from youtubesearchpython import VideosSearch
import asyncio 
load_dotenv('.env')
TOKEN = os.getenv('DISCORD_TOKEN')
BOT_CLIENT_ID = int(os.getenv('BOT_CLIENT_ID'))
print("Token found in the environment. Please hold while we launch Jahnel and get her online. First 4 Chars of TOKEN are", TOKEN[0:4])

intents = discord.Intents.all()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize the queue as a deque
queue = deque()


class CaseInsensitiveBot(commands.Bot):
    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or CaseInsensitiveContext)

    async def get_command(self, command_name):
        # Convert the command to lowercase before checking
        return super().get_command(command_name.lower())

class CaseInsensitiveContext(commands.Context):
    async def trigger_typing(self):
        pass  # You can customize this if needed



@bot.event
async def on_ready():
    bot_guilds = []
    for guild in bot.guilds:
        bot_guilds.append(guild.name)
    print(f'Bot is connected to the following guilds: {", ".join(bot_guilds)}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Skip messages sent by the bot itself

    content = message.clean_content

    if is_twitter_url(message.content):
        if re.search(r'https?://(?:www\.)?x\.com/\S+/status/\d+', message.content): # x.com
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
    return re.search(r'https?://(?:www\.)?twitter\.com/\S+/status/\d+', content) or re.search(r'https?://(?:www\.)?x\.com/\S+/status/\d+', content)

def get_video_title(url):
    try:
        with youtube_dl.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown Title')
            return video_title
    except Exception as e:
        print("Unable to resolve vidoe title")
        return url


@bot.command()
async def play(ctx, *, query):
    # Check if the user is in a voice channel
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel to use this command.")
        return

    # Get the voice channel of the user
    voice_channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        # Create a voice client and connect to the voice channel
        vc = await voice_channel.connect()
    
    if query.startswith('http'):
        # Check if the input is a URL
        url = query
    else:
        # Search on YouTube if the input is not a URL
        videos_search = VideosSearch(query, limit = 1)
        results = videos_search.result()['result']
        
        if not results:
            await ctx.send(f"No search results found for {query}.")
            return

        url = results[0]['link']
    #First video
    if len(queue) < 1:
        # Bot is already in a voice channel, add the URL to the queue
        queue.append(url)
        print("appending url")
        print(queue)
        print(len(queue))
    else:
        # Bot is already in a voice channel, add the URL to the queue
        queue.append(url)
        print("appending url")
        print(queue)
        print(len(queue))
        

    if not ctx.voice_client.is_playing() and len(queue) > 0:
        await play_next(ctx)
    else:
        await ctx.send(f"Added {get_video_title(url)} to the queue. Currently {len(queue)} in the queue.")


@bot.command()
async def skip(ctx):
    # Check if the bot is in a voice channel and there's a video playing
    if ctx.voice_client is not None and ctx.voice_client.is_playing():
        # Stop the current video
        ctx.voice_client.stop()
        await play_next(ctx)

async def play_next(ctx):
    if len(queue) > 0:
        url = queue.popleft()
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'extractor-args': ['--extractor', 'youtube:legacy', '--verbose'],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown Title')
            url2 = info['formats'][0]['url']

            try:

                print("Playing audio...")
                ctx.voice_client.play(discord.FFmpegPCMAudio(url2, options='-vn'))
                await ctx.send(f"**Now Playing**: *{video_title}*")
                print("Audio playing.")
                #BUFFER COMMANDS UNTIL CURRENT AUDIO FINISHES OR IS DISCONNECTED
                 # Wait for the audio to finish playing before moving to the next video
                while ctx.voice_client.is_playing():
                    await asyncio.sleep(1)

                # Play the next video in the queue
                await play_next(ctx)

            except Exception as e:
                print(e)
                await ctx.send("Error adding URL to Queue. Please send !stop, then try adding the URL with !play again")
    else:
        await ctx.send("The queue is empty. Use !play to add videos to the queue.")

@bot.command()
async def stop(ctx):
    # Check if the bot is in a voice channel
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
    await ctx.send("Stopping Media Playback. Queue has been emptied")
@bot.command()
async def helpme(ctx):
    # Provide help information for each command
    help_message = (
        "**!play [url]**: Adds a video to the queue and starts playing if the queue is empty.\n"
        "**!skip**: Skips the current video and plays the next one in the queue.\n"
        "**!stop**: Stops playback and disconnects the bot from the voice channel.\n"
        "**!helpme**: Displays this help message. *'You know I'm obsessed with it'* "
    )
    await ctx.send(help_message)


@bot.event
async def on_voice_state_update(member, before, after):
    if bot.voice_clients:
        # Check if the bot is in a voice channel
        voice_channel = bot.voice_clients[0].channel if bot.voice_clients else None

        if voice_channel and len(voice_channel.members) == 1:
            # Disconnect the bot if the voice channel becomes empty
            await bot.voice_clients[0].disconnect()


bot.run(TOKEN)
