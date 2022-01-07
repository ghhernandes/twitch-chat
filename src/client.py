import asyncio
import re
import time
from websockets import connect
from dataclasses import dataclass

from .message import Message
from .user import User

REGX_USER = re.compile(r":(?P<user>.*)!")

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
                        
            await self.authenticate()

            #await self.join_channels([self.channel_name])

            await self._join_channel(self.channel_name)

            print('Connected.')
            await self._keep_alive()
        except:
            await self.close()                    
         

    async def close(self) -> None:
        if not self.is_alive:
            await self._websocket.close()
            await self._websocket.wait_closed()
            print('Connection closed.')


    async def _send(self, msg: str) -> None:
        await self._websocket.send(f"{msg}\r\n")
        

    async def send(self, message: Message) -> None:
        await self._send(f'PRIVMSG {message.text}')


    async def _pong(self, _=None):
        self._last_ping = time.time()
        await self._send("PONG :tmi.twitch.tv\r\n")        


    async def authenticate(self):
        await self._send(f"PASS {self.oauth_token}")
        await self._send(f"NICK {self.bot_username}")
        

    async def join_channels(self, *channels: str):
        for ch in channels:
            # TODO: create asyncio tasks for join in multiple channels (use lock to connect one at once)
            await self._join_channel(ch)


    async def _join_channel(self, channel: str):
        await self._send(f"JOIN #{channel}")


    async def _keep_alive(self) -> None:
        print('keeping alive.')
        while self.is_alive:
            data = await self._websocket.recv()
            parsed = self.data_parser(data)

            # TODO: refactor this shit
            if parsed['action'] == 'PING':
                await self._pong()
            elif parsed['action'] == 'PRIVMSG':
                print(f"{parsed['user']} : {parsed['message']}")
          

    def data_parser(self, data: str):
        groups = data.rsplit()
        action = groups[1]

        user = None
        message = None

        if action in ('PRIVMSG'):
            user = re.search(REGX_USER, groups[0]).group('user')
            message = " ".join(groups[3:]).lstrip(':')
            
        return dict(
            action = action,
            user = user,
            message = message
        )
