import asyncio
import re
import time
import logging

from websockets import connect, ConnectionClosedError, ConnectionClosedOK

from .message import Message
from .user import User
from .channel import Channel
from .context import Context
from .exceptions import SocketConnectError, SendMessageError, JoinChannelError, ParseDataError

REGX_USER = re.compile(r":(?P<user>.*)!")

log = logging.getLogger(__name__)


class WebSocketConnection:    
    def __init__(
        self, 
        bot_username: str,
        channel_name: str, 
        oauth_token: str,
        client = None,
        loop = None
    ) -> None:

        self.bot_username = bot_username
        self.channel_name = channel_name
        self.oauth_token = oauth_token
        self._client = client
        self._loop = loop
        self._websocket = None
        self.host = "wss://irc-ws.chat.twitch.tv:443"
        self._actions = {
            'PING': self._pong,
            'PRIVMSG': self._privmsg
        }
        if self._loop is None:
            self._loop = asyncio.get_event_loop()

    @property
    def is_alive(self) -> bool:
        return self._websocket is not None and not self._websocket.closed

    async def connect(self) -> None:
        if self.is_alive:
            await self.close()
        try:
            log.debug('Connecting...')
            self._websocket = await connect(self.host)

            await self.authenticate()

            # await self.join_channels([self.channel_name])

            await self._join_channel(self.channel_name)

            self._loop.create_task(self.dispatch('connect'))

            self._loop.create_task(self._keep_alive())
        except Exception as e:
            await self.close()
            raise SocketConnectError('Socket connection error', e)

    async def close(self) -> None:
        if self.is_alive:
            await self._websocket.close()
            await self._websocket.wait_closed()
            self._websocket = None
            self._loop.create_task(self.dispatch('close'))          
            
    async def send(self, msg: str) -> None:
        try:
            await self._websocket.send(f"{msg}\r\n")
        except Exception as e:
            raise SendMessageError('Send message error', e)

    async def authenticate(self):
        await self.send(f"PASS {self.oauth_token}")
        await self.send(f"NICK {self.bot_username}")

    async def join_channels(self, *channels: str):
        for ch in channels:
            # TODO: create asyncio tasks for join in multiple channels (use lock to connect one at once)
            await self._join_channel(ch)

    async def _join_channel(self, channel: str):
        try:
            await self.send(f"JOIN #{channel}")
        except Exception as e:
            raise JoinChannelError('Join channel error', e)

    async def _keep_alive(self) -> None:
        log.debug('Keeping alive')
        try:
            while self.is_alive:
                data = await self._websocket.recv()
                if data:
                    parsed = self._parser(data)
                    self._loop.create_task(self._process_data(parsed))
        except ConnectionClosedOK:
            pass
        except ConnectionClosedError:
            self._loop.create_task(self.connect())        

    async def dispatch(self, event: str, **kwargs):
        log.debug(f"Dispatching event {event}")
        ctx = Context(**kwargs)
        await self._client.run_event(event, ctx)

    async def _pong(self, _=None):
        self._last_ping = time.time()
        await self.send("PONG :tmi.twitch.tv\r\n")

    async def _privmsg(self, data):
        user = User(username=data['user'])
        channel = Channel(name=data['channel'])
        message = Message(
            raw_data=data, 
            channel=channel,
            user=user,
            text=data['message']
            )
        await self.dispatch('message', message=message)

    async def _process_data(self, parsed):
        action = parsed['action']
        if action in self._actions:
            await self._actions[action](parsed)
        
    def _parser(self, data):
        try:
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
        except Exception as e:
            raise ParseDataError('Parse data error', e)
