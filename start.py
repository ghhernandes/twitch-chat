import os
from dotenv import load_dotenv
from rich.console import Console

from src.bot import Bot

load_dotenv()

BOT_USERNAME = os.getenv('BOT_USERNAME')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')

client = Bot(BOT_USERNAME, CHANNEL_NAME, OAUTH_TOKEN)
console = Console()

@client.event('message')
async def on_message(ctx):
    console.print(f"[bold cyan]{ctx.message.user.username}:[/bold cyan] {ctx.message.text}")

@client.event('connect')
async def on_connect(ctx):
    console.print('[bold green]Connected![/bold green]')

@client.event('close')
async def on_close(ctx):
    console.print('[bold red]Connection closed.[/bold red]')    

@client.command('!close')
async def command_close(ctx):
    await client.close()

if __name__ == '__main__':
    client.run()    