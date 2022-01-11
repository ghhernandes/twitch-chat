import asyncio
import re
import time

from websockets import connect
from dataclasses import dataclass

REGX_USER = re.compile(r":(?P<user>.*)!")

@dataclass
class WebSocketConnection:
    bot_username: str
    channel_name: str
    oauth_token: str
            
    @property
    def is_alive(self) -> bool:
        return self._websocket is not None and not self._websocket.closed


    async def connect(self) -> None:
        self._websocket = None
        
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
        if self.is_alive:
            await self._websocket.close()
            await self._websocket.wait_closed()
            print('Connection closed.')


    async def _send(self, msg: str) -> None:
        await self._websocket.send(f"{msg}\r\n")
    

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
            parsed = self._parser(data)

            # TODO: refactor this shit
            if parsed['action'] == 'PING':
                await self._pong()
            elif parsed['action'] == 'PRIVMSG':
                print(f"{parsed['user']} : {parsed['message']}")
          
    def _parser(self, data):
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