import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import os
import logging
import random
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import asyncio

# Import the keep_alive function from webserver.py
from webserver import keep_alive

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Get the bot token and channel ID from environment variables
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
NEWS_CHANNEL_ID = int(os.getenv('NEWS_CHANNEL_ID'))  # Convert Channel ID to integer

# Define the bot's intents
intents = discord.Intents.default()
intents.messages = True  # Enable message-related events
intents.message_content = True  # Enable access to message content (required for commands)

# Create a bot instance with the required intents
bot = commands.Bot(command_prefix="!", intents=intents)

<<<<<<< HEAD
# Function to scrape PC Gamer (requests + BeautifulSoup)
async def scrape_pc_gamer(limit=5):
=======
# Call keep_alive() before running the bot to start the web server
keep_alive()

# Function to scrape top-rated gaming news from multiple sources
def scrape_top_gaming_news():
>>>>>>> 680f9cdf983a28a1dc86db0343f224e2989888bd
    all_news = []
    try:
        logging.info("Scraping PC Gamer...")
        pcgamer_url = 'https://pcgamer.com/games/'
        response = requests.get(pcgamer_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        pcgamer_articles = soup.find_all('div', class_='listingResult small result1', limit=limit)
        logging.info(f"PC Gamer articles found: {len(pcgamer_articles)}")

        for article in pcgamer_articles:
            title = article.find('h3', class_='article-name').text.strip()
            if "Wordle" in title:  # Filter out irrelevant content
                continue
            link = article.find('a')['href']
            all_news.append(f"PC Gamer: {title} - {link}")
    except Exception as e:
        logging.error(f"Error scraping PC Gamer: {e}")
    return all_news


# Function to scrape PlayStation Blog with async Playwright or requests fallback
async def scrape_playstation_blog(limit=5):
    all_news = []
    try:
        # Try using Playwright
        logging.info("Scraping PlayStation Blog using Playwright...")
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://blog.playstation.com/')
            
            # Wait for broader content to load and then search for titles
            await page.wait_for_selector('article', timeout=15000)
            
            page_source = await page.content()
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Let's try targeting 'h2' and find the nearest <a> for the link
            ps_blog_articles = soup.find_all('h2', limit=limit)
            logging.info(f"PlayStation Blog articles found: {len(ps_blog_articles)}")

            for article in ps_blog_articles:
                title = article.text.strip()
                # Find the closest <a> tag and make sure it contains a link
                link_tag = article.find_parent('a')
                if not link_tag or not link_tag.get('href'):
                    link_tag = article.find_next('a')
                
                link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else "No link found"
                if link.startswith('/'):
                    link = f"https://blog.playstation.com{link}"
                all_news.append(f"PlayStation Blog: {title} - {link}")
            
            await browser.close()
    except Exception as e:
        logging.error(f"Error scraping PlayStation Blog with Playwright: {e}")
        logging.info("Falling back to requests for PlayStation Blog...")
        try:
            # Fallback to requests if Playwright fails
            ps_blog_url = 'https://blog.playstation.com/'
            response = requests.get(ps_blog_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            ps_blog_articles = soup.find_all('h2', limit=limit)
            logging.info(f"PlayStation Blog articles found: {len(ps_blog_articles)}")

            for article in ps_blog_articles:
                title = article.text.strip()
                link_tag = article.find_parent('a')
                if not link_tag or not link_tag.get('href'):
                    link_tag = article.find_next('a')
                
                link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else "No link found"
                if link.startswith('/'):
                    link = f"https://blog.playstation.com{link}"
                all_news.append(f"PlayStation Blog: {title} - {link}")
        except Exception as e:
            logging.error(f"Error scraping PlayStation Blog with requests: {e}")

    return all_news


# Function to scrape The Verge with async Playwright or requests fallback
async def scrape_the_verge(limit=5):
    all_news = []
    try:
        # Try using Playwright
        logging.info("Scraping The Verge using Playwright...")
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://www.theverge.com/games')
            await page.wait_for_selector('h1', timeout=15000)  # Increase timeout
            page_source = await page.content()
            soup = BeautifulSoup(page_source, 'html.parser')
            verge_articles = soup.find_all('h1', limit=limit)
            logging.info(f"The Verge articles found: {len(verge_articles)}")

            for article in verge_articles:
                title = article.text.strip()

                # Find the correct <a> tag linked to the article
                link_tag = article.find_parent('a')
                if not link_tag or not link_tag.get('href'):
                    link_tag = article.find_next('a')

                link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else "No link found"

                if link != "No link found":
                    link = f"https://www.theverge.com{link}" if link.startswith('/') else link

                all_news.append(f"The Verge: {title} - {link}")
            await browser.close()
    except Exception as e:
        logging.error(f"Error scraping The Verge with Playwright: {e}")
        logging.info("Falling back to requests for The Verge...")
        try:
            # Fallback to requests if Playwright fails
            verge_url = 'https://www.theverge.com/games'
            response = requests.get(verge_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            verge_articles = soup.find_all('h1', limit=limit)
            logging.info(f"The Verge articles found: {len(verge_articles)}")

            for article in verge_articles:
                title = article.text.strip()
                link_tag = article.find_parent('a')
                if not link_tag or not link_tag.get('href'):
                    link_tag = article.find_next('a')

                link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else "No link found"

                if link != "No link found":
                    link = f"https://www.theverge.com{link}" if link.startswith('/') else link

                all_news.append(f"The Verge: {title} - {link}")
        except Exception as e:
            logging.error(f"Error scraping The Verge with requests: {e}")

    return all_news


# Function to scrape Gamer Rant with async Playwright
async def scrape_gamer_rant_with_playwright(limit=5):
    all_news = []
    try:
        async with async_playwright() as p:
            logging.info("Scraping Gamer Rant using Playwright...")
            browser = await p.firefox.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://gamerant.com/')
            await page.wait_for_timeout(5000)
            page_source = await page.content()
            soup = BeautifulSoup(page_source, 'html.parser')
            gamer_rant_articles = soup.find_all('h2', limit=limit)
            logging.info(f"Gamer Rant articles found: {len(gamer_rant_articles)}")

            for article in gamer_rant_articles:
                title = article.text.strip()
                link_tag = article.find_parent('a')
                if not link_tag or not link_tag.get('href'):
                    link_tag = article.find_next('a')
                link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else "No link found"
                if link.startswith('/'):
                    link = f"https://gamerant.com{link}"
                logging.info(f"Attempting to post: Gamer Rant: {title} - {link}")  # Add logging
                all_news.append(f"Gamer Rant: {title} - {link}")
            await browser.close()
    except Exception as e:
        logging.error(f"Error scraping Gamer Rant with Playwright: {e}")

    return all_news


# Function to aggregate all news from different sources in parallel
async def scrape_top_gaming_news(limit=5):
    results = await asyncio.gather(
        scrape_pc_gamer(limit),
        scrape_playstation_blog(limit),
        scrape_the_verge(limit),
        scrape_gamer_rant_with_playwright(limit)
    )
    all_news = [item for sublist in results for item in sublist]  # Flatten the results
    return all_news


# Event: on_ready
@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")
    random_post_news.start()  # Start the task loop when the bot is ready


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

    news_items = await scrape_top_gaming_news()

    logging.info(f"News items to post: {len(news_items)}")

    if news_items:
        for item in news_items:
            logging.info(f"Attempting to post: {item}")
            await channel.send(item)
    else:
        await channel.send("No new top-rated news at the moment!")


# Command: Get latest news on demand
@bot.command(name="news")
async def news(ctx):
    logging.info("User requested news on demand.")
    news_items = await scrape_top_gaming_news()

    logging.info(f"News items to post: {len(news_items)}")  # Log the items being posted

    if news_items:
        for item in news_items:
            await ctx.send(item)
    else:
        await ctx.send("No new top-rated news at the moment!")


# Run the bot with the token from the environment variable
bot.run(DISCORD_BOT_TOKEN)
