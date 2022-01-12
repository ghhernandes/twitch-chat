import re
import time

from websockets import connect

REGX_USER = re.compile(r":(?P<user>.*)!")

class WebSocketConnection:
    
    def __init__(
        self, 
        bot_username: str,
        channel_name: str, 
        oauth_token: str,
        client = None
        ) -> None:
        self.bot_username = bot_username
        self.channel_name = channel_name
        self.oauth_token = oauth_token
        self._client = client

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

            # await self.join_channels([self.channel_name])

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

    async def send(self, msg: str) -> None:
        await self._websocket.send(f"{msg}\r\n")

    async def _pong(self, _=None):
        self._last_ping = time.time()
        await self.send("PONG :tmi.twitch.tv\r\n")

    async def authenticate(self):
        await self.send(f"PASS {self.oauth_token}")
        await self.send(f"NICK {self.bot_username}")

    async def join_channels(self, *channels: str):
        for ch in channels:
            # TODO: create asyncio tasks for join in multiple channels (use lock to connect one at once)
            await self._join_channel(ch)

    async def _join_channel(self, channel: str):
        await self.send(f"JOIN #{channel}")

    async def _keep_alive(self) -> None:
        print('keeping alive.')
        while self.is_alive:
            data = await self._websocket.recv()
            parsed = self._parser(data)

            if parsed['action'] == 'PING':
                await self._pong()
            elif parsed['action'] == 'PRIVMSG':
                self.on_receive_message(parsed['channel'], parsed['user'], parsed['message'])

    def on_receive_message(self, channel, user, message):
        print(f"#{channel} {user}: {message}")

    def _parser(self, data):
        groups = data.rsplit()
        action = groups[1]

        channel = None
        user = None
        message = None

        if action in ('PRIVMSG'):
            channel = ''
            user = re.search(REGX_USER, groups[0]).group('user')
            message = " ".join(groups[3:]).lstrip(':')

        return dict(
            action=action,
            channel=channel,
            user=user,
            message=message
        )
