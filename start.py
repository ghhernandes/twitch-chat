import os
from dotenv import load_dotenv
from rich.console import Console

from src.bot import Bot
from src.context import Context
from src.message import Message

load_dotenv()

BOT_USERNAME = os.getenv('BOT_USERNAME')
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')
CHANNEL = os.getenv('CHANNEL')

client = Bot(BOT_USERNAME, [CHANNEL], OAUTH_TOKEN)
console = Console()

@client.event('message')
async def on_message(ctx: Context):
    message = ctx.get_message()
    console.print(f"[bold blue]{message.channel.name}[/bold blue] [bold cyan]{message.user.username}:[/bold cyan] {message.text}")

@client.event('connect')
async def on_connect(ctx: Context):
    console.print('[bold green]Connected![/bold green]')

@client.event('ping')
async def on_ping(ctx: Context):
    last_ping = ctx.get_last_ping()
    console.print(f'[bold red]PING from server. (Last: {last_ping})[/bold red]')

@client.event('close')
async def on_close(ctx: Context):
    console.print('[bold red]Connection closed.[/bold red]')    

@client.command('!hello')
async def command_close(ctx: Context):
    client.reply(ctx.message.channel.name, f'Hello @{ctx.message.user.username}!')

if __name__ == '__main__':
    client.run()    