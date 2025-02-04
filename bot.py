import discord
from discord.ext import commands, tasks
import os
import feedparser
import logging
import random
from datetime import datetime
from dotenv import load_dotenv
import asyncio
from discord.errors import HTTPException

# Import keep_alive from webserver.py to keep the bot alive on deployment
from webserver import keep_alive

# Load environment variables from .env file
load_dotenv()

# Get the bot token and channel ID from environment variables
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
NEWS_CHANNEL_ID = os.getenv('NEWS_CHANNEL_ID')

# Check for missing environment variables
if not DISCORD_BOT_TOKEN or not NEWS_CHANNEL_ID:
    raise ValueError("DISCORD_BOT_TOKEN or NEWS_CHANNEL_ID is missing from the environment variables")

NEWS_CHANNEL_ID = int(NEWS_CHANNEL_ID)  # Convert Channel ID to integer

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the bot's intents
intents = discord.Intents.default()
intents.messages = True  # Enable message-related events
intents.message_content = True  # Enable access to message content (required for commands)

# Create a bot instance with the required intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Call keep_alive to start the web server
keep_alive()

# RSS Feeds array for news
RSS_FEEDS = [
    "https://www.pcgamer.com/rss/",
    "https://blog.playstation.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://gamerant.com/feed/"
]

# Function to pull news from RSS feeds and return latest articles
def get_latest_news():
    news_items = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:3]:  # Get the latest 3 articles from each feed
            news_items.append(f"**{entry.title}**\n{entry.link}")
    return news_items

# Event: on_ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    # Ensure loop task starts
    if not random_post_news.is_running():
        random_post_news.start()
    
    channel = bot.get_channel(NEWS_CHANNEL_ID)  # Use correct channel ID
    if channel:
        news = get_latest_news()
        for article in news:
            await channel.send(article)
    else:
        print("Channel not found!")

# New: Event when the bot connects to Discord
@bot.event
async def on_connect():
    logging.info("Bot connected to Discord.")

# New: Event when the bot disconnects from Discord
@bot.event
async def on_disconnect():
    logging.info("Bot disconnected from Discord.")

# Task: Automatically post news at random intervals between 9 AM and 9 PM
@tasks.loop(minutes=60)
async def random_post_news():
    current_time = datetime.now().time()

    # Define active hours range
    start_time = datetime.strptime("09:00", "%H:%M").time()
    end_time = datetime.strptime("21:00", "%H:%M").time()

    # Check if current time is within the active hours range
    if start_time <= current_time <= end_time:
        # Decide randomly whether to post news in this hour
        if random.choice([True, False]):  # 50% chance to post
            await post_news_to_channel()

async def post_news_to_channel():
    channel = bot.get_channel(NEWS_CHANNEL_ID)
    if channel is None:
        logging.error(f"Failed to find the channel with ID {NEWS_CHANNEL_ID}.")
        return

    news_items = get_latest_news()

    logging.info(f"News items to post: {len(news_items)}")

    if news_items:
        for item in news_items:
            logging.info(f"Attempting to post: {item}")
            await channel.send(item)
    else:
        await channel.send("No new articles at the moment!")

# Command: Get latest news on demand
@bot.command(name="news")
async def news(ctx):
    logging.info("User requested news on demand.")
    news_items = get_latest_news()

    logging.info(f"News items to post: {len(news_items)}")  # Log the items being posted

    if news_items:
        for item in news_items:
            await ctx.send(item)
    else:
        await ctx.send("No new articles at the moment!")

# Run the bot with the token from the environment variable
async def run_bot():
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            await bot.start(DISCORD_BOT_TOKEN)
            break  # Exit loop if successful
        except HTTPException as e:
            if e.status == 429:
                retry_after = e.retry_after
                logging.error(f"Rate limited. Retrying after {retry_after} seconds. Retry attempt {retry_count + 1}/{max_retries}")
                await asyncio.sleep(retry_after)
                retry_count += 1
        except Exception as e:
            retry_count += 1
            wait_time = min(60, 2 ** retry_count)  # Exponential backoff, max 60 sec
            logging.exception(f"Unhandled exception. Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
    
    # Final cleanup before shutdown
    try:
        await bot.close()
    except Exception as e:
        logging.exception("Error closing the bot:")

