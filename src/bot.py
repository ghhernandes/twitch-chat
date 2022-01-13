
from .client import Client
from .context import Context

class Bot(Client):
    def __init__(self, username: str, channel: str, oauth: str) -> None:
        super().__init__(username, channel, oauth)
        self.commands = {}
 
    def command(self, command):
        def decorate(fn):
            self._add_command(command, fn)            
        return decorate

    def _add_command(self, command: str, func):
        if not command in self.commands:
            self.commands[command] = func

    async def run_event(self, event: str, ctx: Context) -> None:
        if event == 'message':
            command = ctx.message.text.split()[0]
            if command in self.commands:
                self.loop.create_task(self.commands[command](ctx))