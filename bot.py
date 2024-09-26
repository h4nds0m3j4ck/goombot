import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Import the keep_alive function from webserver.py
from webserver import keep_alive

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

# Call keep_alive() before running the bot to start the web server
keep_alive()

# Function to scrape top-rated gaming news from multiple sources
def scrape_top_gaming_news():
    all_news = []

    # Scrape PC Gamer
    print("Scraping PC Gamer...")
    pcgamer_url = 'https://pcgamer.com/games/'
    response = requests.get(pcgamer_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    for article in soup.find_all('div', class_='listingResult small result1'):
        title = article.find('h3', class_='article-name').text.strip()
        link = article.find('a')['href']
        all_news.append(f"PC Gamer: {title} - {link}")
    print(f"PC Gamer articles found: {len(all_news)}")

    # Scrape PlayStation Blog
    print("Scraping PlayStation Blog...")
    ps_blog_url = 'https://blog.playstation.com/'
    response = requests.get(ps_blog_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find articles with the updated structure (h1 with class post-single__title)
    ps_blog_articles = soup.find_all('h1', class_='post-single__title')
    print(f"PlayStation Blog articles found: {len(ps_blog_articles)}")

    for article in ps_blog_articles:
        title = article.text.strip()

        # Find the link associated with the article
        link_tag = article.find('a')
        link = link_tag['href'] if link_tag else "No link found"

        all_news.append(f"PlayStation Blog: {title} - {link}")

    # Scrape The Verge
    print("Scraping The Verge...")
    verge_url = 'https://www.theverge.com/games'
    response = requests.get(verge_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find articles with the new class structure (h1 with specific classes)
    verge_articles = soup.find_all('h1',
                                   class_='mb-28 hidden max-w-[900px] font-polysans text-45 font-bold leading-100 selection:bg-franklin-20 lg:block')
    print(f"The Verge articles found: {len(verge_articles)}")

    for article in verge_articles:
        title = article.text.strip()

        # Find the link associated with the article
        link_tag = article.find('a')
        link = link_tag['href'] if link_tag else "No link found"

        all_news.append(f"The Verge: {title} - {link}")

    # Scrape Gamer Rant
    print("Scraping Gamer Rant...")
    gamer_rant_url = 'https://gamerant.com/'
    response = requests.get(gamer_rant_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find articles with the updated structure (h1 with class article-header-title)
    gamer_rant_articles = soup.find_all('h1', class_='article-header-title')
    print(f"Gamer Rant articles found: {len(gamer_rant_articles)}")

    for article in gamer_rant_articles:
        title = article.text.strip()

        # Find the link associated with the article
        link_tag = article.find('a')
        link = link_tag['href'] if link_tag else "No link found"

        all_news.append(f"Gamer Rant: {title} - {link}")

    # Return the list of all news
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
    if channel is None:
        print(f"Failed to find the channel with ID {NEWS_CHANNEL_ID}.")
        return

    news_items = scrape_top_gaming_news()

    print(f"News items to post: {len(news_items)}")

    if news_items:
        for item in news_items:
            print(f"Attempting to post: {item}")
            await channel.send(item)  # Send the news item to the channel
    else:
        await channel.send("No new top-rated news at the moment!")


# Run the bot with the token from the environment variable
bot.run(DISCORD_BOT_TOKEN)
