import asyncio

from src.context import Context

from .websocket import WebSocketConnection
from .message import Message
from .exceptions import EventNotExistError

class Client:
    def __init__(self, username: str, channel: str, oauth: str) -> None:
        self.username = username
        self.channel = channel
        self.oauth = oauth
        self._events = {
            'message': None
        }

    def run(self) -> None:
        self.loop = asyncio.get_event_loop()
        self._connection = WebSocketConnection(
            bot_username=self.username, 
            channel_name=self.channel, 
            oauth_token=self.oauth, 
            client=self, 
            loop=self.loop)        

        try:
            self.loop.create_task(self.connect())
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.loop.run_until_complete(self.close())
            self.loop.close()

    def event(self, command):
        def decorate(fn):
            self._add_event(command, fn)            
        return decorate

    def _add_event(self, event: str, func):
        if event not in self._events:
            raise EventNotExistError("Event not exists.")
        self._events[event] = func

    async def connect(self) -> None:
        await self._connection.connect()

    async def close(self) -> None:
        await self._connection.close()

    async def send(self, message: Message) -> None:
        await self._connection.send(f'PRIVMSG {message.text}')

    async def run_event(self, event: str, ctx: Context) -> None:
        if event in self._events:
            self.loop.create_task(self._events[event](ctx))
