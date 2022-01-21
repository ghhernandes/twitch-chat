import asyncio
import re
import time
import logging

from websockets import connect, ConnectionClosedError, ConnectionClosedOK
from typing import Any

from .message import Message
from .user import User
from .channel import Channel
from .context import Context
from .exceptions import SocketConnectError, SendMessageError, JoinChannelError, ParseDataError, ChannelLimitExceededError

REGX_USER = re.compile(r":(?P<user>.*)!")

MAX_CHANNEL_JOIN = 5

log = logging.getLogger(__name__)

class WebSocketConnection:    
    def __init__(
        self, 
        bot_username: str,
        oauth_token: str,
        channels: list[str],
        client: Any = None,
        loop: asyncio.AbstractEventLoop = None
    ) -> None:
        self.bot_username = bot_username
        self.oauth_token = oauth_token
        self.channels = channels
        self._client = client
        self._loop = loop
        self._websocket: Any = None
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
            
            self._loop.create_task(self.dispatch('connect'))

            self._loop.create_task(self._join_channels(self.channels))
            
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

    async def _join_channels(self, channels):
        for ch in channels:
            await self.join_channel(ch)

    async def join_channel(self, channel: str):
        try:
            if len(self.channels) > MAX_CHANNEL_JOIN:
                raise ChannelLimitExceededError('Max Channels joined limit exceeded.')
            await self.send(f"JOIN #{channel}")
            await self.dispatch('join', channel=channel)
        except Exception as e:
            self.channels.remove(channel)
            raise JoinChannelError('Join channel error', e)

    async def leave_channel(self, channel: str):
        if channel in self.channels:
            await self.send(f"PART #{channel}")
            self.channels.remove(channel)
            await self.dispatch('part', channel=channel)            
        
    async def _keep_alive(self) -> None:
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
        await self.dispatch('ping', last=self._last_ping)

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
        
    def _parser(self, data: str):
        log.debug(data)
        try:
            groups = data.rsplit()
            action = 'PING' if data.startswith('PING') else groups[1]

            channel = None
            user = None
            message = None

            if action in ('PRIVMSG'):
                user = re.search(REGX_USER, groups[0]).group('user')
                channel = groups[2]
                message = " ".join(groups[3:]).lstrip(':')
            
            return dict(
                action=action,
                channel=channel,
                user=user,
                message=message
            )
        except Exception as e:
            raise ParseDataError('Parse data error', e)
