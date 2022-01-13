## Twitch Chat

Twitch Chat with Python, Asyncio and WebSockets

```python

from src.client import Client

@client.event('message')
async def on_message(ctx):
    print(f"{ctx.message.user.username}: {ctx.message.text}")

if __name__ == '__main__':
    chat = Client(BOT_USERNAME, CHANNEL_NAME, OAUTH_TOKEN)
    chat.run()

```