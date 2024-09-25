import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the bot token and channel ID from environment variables
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
NEWS_CHANNEL_ID = int(os.getenv('NEWS_CHANNEL_ID'))  # Convert Channel ID to integer

# Define the bot's intents
intents = discord.Intents.default()
intents.messages = True  # Enable message-related events
intents.message_content = True  # Enable access to message content (required for commands)

# Create a bot instance with the required intents
bot = commands.Bot(command_prefix="!", intents=intents)


# Function to scrape top-rated gaming news from multiple sources
def scrape_top_gaming_news():
    all_news = []

    # Scrape PC Gamer
    pcgamer_url = 'https://pcgamer.com/games/'
    response = requests.get(pcgamer_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    for article in soup.find_all('div', class_='listingResult small result1'):
        title = article.find('h3', class_='article-name').text.strip()
        link = article.find('a')['href']
        all_news.append(f"PC Gamer: {title} - {link}")

    # Scrape PlayStation Blog
    ps_blog_url = 'https://blog.playstation.com/'
    response = requests.get(ps_blog_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find articles with the updated structure (h1 with class post-single__title)
    for article in soup.find_all('h1', class_='post-single__title'):
        title = article.text.strip()
        link = article.find_parent('a')['href']  # Assuming the article title is within an <a> parent link
        all_news.append(f"PlayStation Blog: {title} - {link}")

    # Scrape The Verge (updated)
    verge_url = 'https://www.theverge.com/games'
    response = requests.get(verge_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find articles with the new class structure (h1 with specific classes)
    for article in soup.find_all('h1', class_='mb-28 hidden max-w-[900px] font-polysans text-45 font-bold leading-100 selection:bg-franklin-20 lg:block'):
        title = article.text.strip()
        link = article.find_parent('a')['href']  # Assuming the link is in the parent <a> tag
        all_news.append(f"The Verge: {title} - {link}")

    # Scrape Gamer Rant (updated)
    gamer_rant_url = 'https://gamerant.com/'
    response = requests.get(gamer_rant_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find articles with the updated structure (h1 with class article-header-title)
    for article in soup.find_all('h1', class_='article-header-title'):
        title = article.text.strip()
        link = article.find_parent('a')['href']  # Assuming the article title is within an <a> parent link
        all_news.append(f"Gamer Rant: {title} - {link}")

    return all_news


# Event: on_ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    post_news.start()  # Start the task loop when the bot is ready


# Task: Automatically post news every 24 hours
@tasks.loop(hours=24)
async def post_news():
    channel = bot.get_channel(NEWS_CHANNEL_ID)
    news_items = scrape_top_gaming_news()

    if news_items:
        for item in news_items:
            await channel.send(item)
    else:
        await channel.send("No new top-rated news at the moment!")


# Run the bot with the token from the environment variable
bot.run(DISCORD_BOT_TOKEN)
