import os
from dotenv import load_dotenv

from src.bot import Bot

load_dotenv()

BOT_USERNAME = os.getenv('BOT_USERNAME')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')

client = Bot(BOT_USERNAME, CHANNEL_NAME, OAUTH_TOKEN)

@client.event('message')
async def on_message(ctx):
    print(f"{ctx.message.user.username}: {ctx.message.text}")

@client.command('!close')
async def on_teste(ctx):
    print(f"{ctx.message.user.username} used command !close")
    await client.close()

if __name__ == '__main__':
    client.run()    