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

# Import keep_alive from webserver.py
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

# Call the keep_alive function to start the web server
keep_alive()

# Function to scrape PC Gamer (requests + BeautifulSoup)
async def scrape_pc_gamer(limit=5):
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
        logging.info("Scraping PlayStation Blog using Playwright...")
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://blog.playstation.com/')
            await page.wait_for_selector('article', timeout=15000)

            page_source = await page.content()
            soup = BeautifulSoup(page_source, 'html.parser')

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

            await browser.close()
    except Exception as e:
        logging.error(f"Error scraping PlayStation Blog with Playwright: {e}")
        logging.info("Falling back to requests for PlayStation Blog...")
        try:
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

# Remaining scraping functions and logic...

# Run the bot with the token from the environment variable
bot.run(DISCORD_BOT_TOKEN)
