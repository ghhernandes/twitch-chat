import asyncio

from .events import EventHandler
from .websocket import WebSocketConnection
from .message import Message


class Client:
    def __init__(self, username: str, channel: str, oauth: str) -> None:
        self.username = username
        self.channel = channel
        self.oauth = oauth

    def run(self) -> None:
        self.connection = WebSocketConnection(self.username, self.channel, self.oauth, client=self)
        self.event_handler = EventHandler()
        self.loop = asyncio.get_event_loop()
        try:
            self.loop.create_task(self.connect())
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.loop.run_until_complete(self.close())
            self.loop.close()

    async def connect(self) -> None:
        await self.connection.connect()

    async def close(self) -> None:
        await self.connection.close()

    async def send(self, message: Message) -> None:
        await self.connection.send(f'PRIVMSG {message.text}')

    async def run_event(self, event, *args, **kwargs) -> None:
        pass
