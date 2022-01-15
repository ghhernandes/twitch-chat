import os
from dotenv import load_dotenv
from rich.console import Console

from src.bot import Bot

load_dotenv()

BOT_USERNAME = os.getenv('BOT_USERNAME')
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')
CHANNEL = os.getenv('CHANNEL')

client = Bot(BOT_USERNAME, [CHANNEL], OAUTH_TOKEN)
console = Console()

@client.event('message')
async def on_message(ctx):
    console.print(f"[bold blue]{ctx.message.channel.name:<15}[/bold blue] [bold cyan]{ctx.message.user.username}:[/bold cyan] {ctx.message.text}")

@client.event('connect')
async def on_connect(ctx):
    console.print('[bold green]Connected![/bold green]')

@client.event('ping')
async def on_ping(ctx):
    console.print(f'[bold orange]PING from server. (Last: {ctx.last})[/bold orange]')

@client.event('close')
async def on_close(ctx):
    console.print('[bold red]Connection closed.[/bold red]')    

@client.command('!close')
async def command_close(ctx):
    await client.close()

if __name__ == '__main__':
    client.run()    