# Use the official Python image as the base
FROM python:3.11-slim

# Install system dependencies required by Playwright
RUN apt-get update && apt-get install -y \
    libgstreamer-gl1.0-0 \
    libgstreamer-plugins-bad1.0-0 \
    libenchant-2-2 \
    libsecret-1-0 \
    libmanette-0.2-0 \
    libgles2-mesa

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install

# Copy the rest of the application
COPY . /app

# Expose port (if needed, depending on your app's setup)
EXPOSE 8000

# Command to start the bot
CMD ["python", "bot.py"]
