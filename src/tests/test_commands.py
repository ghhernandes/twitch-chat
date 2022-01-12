from functools import wraps

class Bot:
    def __init__(self) -> None:
        self.commands = {}

    def command(self, command):
        def decorate(fn):
            self._add_command(command, fn)            
        return decorate

    def _add_command(self, command: str, func):
        if not command in self.commands:
            self.commands[command] = func

    def execute(self):
        for command in self.commands:
            self.commands[command](None)

bot = Bot()

@bot.command('!help')
def help_command(ctx):
    print('!help')

@bot.command('!setup')
def setup_command(ctx):
    print('!setup')

print(bot.commands.keys())

bot.execute()