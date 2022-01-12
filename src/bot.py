
from .client import Client

class Bot(Client):

    def __init__(self, bot_username, channel_name, oauth_token):
        self.bot_username = bot_username
        self.channel_name = channel_name
        self.oauth_token = oauth_token
        self.commands = {}

    def command(self, command):
        def decorate(fn):
            self._add_command(command, fn)            
        return decorate

    def _add_command(self, command: str, func):
        if not command in self.commands:
            self.commands[command] = func