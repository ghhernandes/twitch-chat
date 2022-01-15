## Twitch Chat

Twitch Chat with Python, Asyncio and WebSockets

```python

from src.bot import Bot

client = Bot(BOT_USERNAME, CHANNEL_NAME, OAUTH_TOKEN)

@client.event('connect')
async def on_connect(ctx):
    print("Connected!")

@client.event('close')
async def on_close(ctx):
    print("Connection closed.")

@client.event('message')
async def on_message(ctx):
    print(f"{ctx.message.user.username}: {ctx.message.text}")

@client.command('!help')
async def help_command(ctx):
    print(f"{ctx.message.user.username} used command !help")

if __name__ == '__main__':
    client.run()
```