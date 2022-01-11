import asyncio
from dataclasses import dataclass

from .websocket import WebSocketConnection
from .message import Message

@dataclass
class Client:
    bot_username: str
    channel_name: str
    oauth_token: str
    
    def run(self):
        self.connection = WebSocketConnection(self.bot_username, self.channel_name, self.oauth_token)
        self.loop = asyncio.get_event_loop()
        try:
            self.loop.create_task(self.connect())
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.loop.run_until_complete(self.close())
            self.loop.close()


    async def connect(self):
        await self.connection.connect()


    async def close(self):
        await self.connection.close()    


    async def send(self, message: Message) -> None:
        await self._send(f'PRIVMSG {message.text}')        