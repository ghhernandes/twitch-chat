from src.client import Client

BOT_USERNAME = ''
CHANNEL_NAME = ''
OAUTH_TOKEN = ''

if __name__ == '__main__':
    chat = Client(BOT_USERNAME, CHANNEL_NAME, OAUTH_TOKEN)
    chat.run()