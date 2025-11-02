import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import asyncio
import aiohttp
import feedparser
from discord.ext import tasks
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
TIKTOK_RSS_URL = os.getenv("TIKTOK_RSS_URL")
YT_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

posted_ids = set()

async def check_and_post_from_feed(channel, session, feed_url, platform_label):
    if not feed_url:
        return
    feed = await fetch_feed(session, feed_url)

    new_entries = []
    for entry in feed.entrues:

        entry_id = getattr(entry, "id", None) or getattr(entry, "link", None) or getattr(entry, "title", None)
        if entry_id and entry_id not in posted_ids:
            new_entries.append(entry)

    for entry in reversed(new_entries):
        entry_id = getattr(entry, "id", None) or getattr(entry, "link", None) or getattr(entry, "title", None)
        title = getattr(entry, "title", "New upload")
        link = getattr(entry, "link", None)
        if link:
            await channel.send(f"**{platform_label}:** {title}\n{link}")
            posted_ids.add(entry_id)

@tasks.loop(minutes=5)
async def poll_socials():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:

        channel = await bot.fetch_channel(CHANNEL_ID)

    async with aiohttp.ClientSession() as session:

        await check_and_post_from_feed(channel, session, YOUTUBE_CHANNEL_ID, "YouTube")

        await check_and_post_from_feed(channel, session, TIKTOK_RSS_URL, "TikTok")

handler = logging.FileHandler(filename='discord.log',encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG) 

@bot.event
async def on_ready():
    print(f"we are ready to go in, {bot.user.name}")
    if not poll_socials.is_running():
        poll_socials.start()