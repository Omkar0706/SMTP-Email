# Import necessary libraries
import os
import asyncio
import aiohttp
import requests
import logging
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()
API_KEY_WEATHER = os.getenv("API_KEY_WEATHER")
API_KEY_NEWS = os.getenv("API_KEY_NEWS")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Configure logging
logging.basicConfig(filename='daily_update.log', level=logging.ERROR)

# Asynchronous function to fetch weather data
async def fetch_weather_async():
    city = "Chennai"  # Replace with the city you want to query
    country = "India"  # Replace with the 2-letter country code (e.g., 'US' for United States)
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={API_KEY_WEATHER}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                logging.error(f"Weather API error: {response.status}")
                return None

# Asynchronous function to fetch news data (all news)
async def fetch_news_async():
    url = f'https://newsapi.org/v2/everything?q=sports&from=2024-11-07&sortBy=publishedAt&apiKey={API_KEY_NEWS}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                logging.error(f"News API error: {response.status}")
                return None

# Function to format data for the email
def format_data(weather_data, news_data):
    formatted_data = "Good Morning,Here's your morning update:\n\n"
    
    if weather_data:
        formatted_data += f"Weather in {weather_data['name']}, {weather_data['sys']['country']}: {weather_data['main']['temp'] - 273.15:.2f}°C, {weather_data['weather'][0]['description']}\n\n"

    if news_data:
        formatted_data += "Top News Headlines:\n"
        for article in news_data['articles'][:5]:  # You can change the number of articles shown
            formatted_data += f"- {article['title']} (Source: {article['source']['name']})\n"
        formatted_data += "\n"
    return formatted_data

# Function to send the email using SMTP
def send_email(subject, body):
    message = MIMEMultipart()
    message["From"] = EMAIL_SENDER
    message["To"] = EMAIL_RECEIVER
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message.as_string())
            print("Email sent successfully")
    except Exception as e:
        logging.error(f"Email sending error: {e}")
        print("Failed to send email")

# Main function to gather data and send the email
async def daily_update():
    # Create async tasks for weather and news data
    weather_task = asyncio.create_task(fetch_weather_async())
    news_task = asyncio.create_task(fetch_news_async())

    # Wait for async tasks to complete
    weather_data = await weather_task
    news_data = await news_task

    # Format data and send email
    email_body = format_data(weather_data, news_data)
    send_email("Your Morning Update", email_body)
    
# Entry point to run the script
if __name__ == "__main__":
    asyncio.run(daily_update())
