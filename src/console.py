from .client import Client
from rich.console import Console

class ConsoleClient(Client):
    def __init__(self, username: str, channel: str, oauth: str) -> None:
        super().__init__(username, channel, oauth)
        self.console = Console()

    @client.event('message')
    async def on_message(ctx):
        console.print(f"[bold cyan]{ctx.message.user.username}:[/bold cyan] {ctx.message.text}")

    @client.event('connect')
    async def on_connect(ctx):
        console.print('[bold green]Connected![/bold green]')

    @client.event('close')
    async def on_close(ctx):
        console.print('[bold red]Connection closed.[/bold red]')    
