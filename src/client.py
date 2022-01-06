import asyncio
from websockets import connect
from dataclasses import dataclass

from .message import Message
from .user import User

@dataclass
class Client:
    bot_username: str
    channel_name: str
    oauth_token: str
      
    def run(self) -> None:
        self._websocket = None
        self.loop = asyncio.get_event_loop()
        try:
            self.loop.create_task(self.connect())
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.loop.run_until_complete(self.close())
            self.loop.close()

    @property
    def is_alive(self) -> bool:
        return self._websocket is not None and not self._websocket.closed

    async def connect(self) -> None:

        if self.is_alive:
            self.close()

        try:
            print("Connecting...")
            self._websocket = await connect("wss://irc-ws.chat.twitch.tv:443")
            print("Sending infos...")
            await self.send(Message(self.channel_name, User(self.bot_username), f"PASS {self.oauth_token}"))
            await self.send(Message(self.channel_name, User(self.bot_username), f"NICK {self.bot_username}"))
            await self.send(Message(self.channel_name, User(self.bot_username), f"JOIN #{self.channel_name}"))

            print('Connected.')
            await self._keep_alive()
        except:
            await self.close()                    
         
    async def close(self) -> None:
        if not self.is_alive:
            await self._websocket.close()
            await self._websocket.wait_closed()
            print('Connection closed.')

    async def send(self, message: Message) -> None:
        await self._websocket.send(message.text)        

    async def _keep_alive(self) -> None:
        print('keeping alive.')
        while self.is_alive:
            print(await self._websocket.recv())
            #data = await self._websocket.read()
            #self._process_data(data)
            #print(f"Received: {data.decode()!r}")
        
    def _process_data(self, data: str) -> None:
        if 'ping' in data:
            self._pong()

    async def _pong(self) -> None:
        await self.send(Message(self.channel_name, User(self.bot_username),'pong'))