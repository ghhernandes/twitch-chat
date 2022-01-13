
from .client import Client
from .context import Context
from .exceptions import CommandExistsError

class Bot(Client):
    def __init__(self, username: str, channel: str, oauth: str) -> None:
        super().__init__(username, channel, oauth)
        self._commands = {}
 
    def command(self, command):
        def decorate(fn):
            self._add_command(command, fn)            
        return decorate

    def _add_command(self, command: str, func):
        if command not in self._commands:
            self._commands[command] = func
        else:
            raise CommandExistsError("Command added before.")
    
    async def run_event(self, event: str, ctx: Context) -> None:
        await super().run_event(event, ctx)

        if event == 'message':
            command = ctx.message.text.split()[0]
            if command in self._commands:
                self.loop.create_task(self._commands[command](ctx))