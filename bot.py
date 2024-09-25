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

# Function to scrape top-rated gaming news from PC Gamer
def scrape_top_gaming_news():
    all_news = []
    
    # URL of the PC Gamer games news page
    url = 'https://pcgamer.com/games/'
    
    # Make a request to the website
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all articles with the class 'listingResult small result1'
    for article in soup.find_all('div', class_='listingResult small result1'):
        # Extract the article title and link
        title = article.find('h3', class_='article-name').text.strip()
        link = article.find('a')['href']
        
        # Append the formatted news article to the list
        all_news.append(f"{title} - {link}")
    
    return all_news

# Event: on_ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
    # Immediate test: Post news as soon as the bot logs in
    await post_news()  # This will trigger an immediate news post

    post_news.start()  # Start the task loop when the bot is ready

# Task: Automatically post news every hour
@tasks.loop(hours=1)
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
