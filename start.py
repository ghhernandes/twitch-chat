import os
from dotenv import load_dotenv

from src.client import Client

load_dotenv()

BOT_USERNAME = os.getenv('BOT_USERNAME')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')

if __name__ == '__main__':
    chat = Client(BOT_USERNAME, CHANNEL_NAME, OAUTH_TOKEN)
    chat.run()