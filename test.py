import asyncio
import os 
import re
from dotenv import load_dotenv

from websockets import connect

load_dotenv()

BOT_USERNAME = os.getenv('BOT_USERNAME')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')

REGX_USER = re.compile(r":(?P<user>.*)!")

async def _keep_alive(websocket):
    print('keeping alive.')
    try:
        while True:
            data = await websocket.recv()
            user, message = parse_message(data)
            print(f"{user}: {message}")
    except KeyboardInterrupt:
        pass
    finally:
        await websocket.close()
        await websocket.wait_closed()


def parse_message(data: str):
    groups = data.rsplit()
    action = groups[1]

    user = None
    message = None

    if action in ('PRIVMSG'):
        user = re.search(REGX_USER, groups[0]).group('user')
        message = " ".join(groups[3:]).lstrip(':')
        
    return user, message
            

async def main():
    print("Connecting")
    websocket = await connect('wss://irc-ws.chat.twitch.tv:443')
    await websocket.send(f"PASS {OAUTH_TOKEN}")
    await websocket.send(f"NICK {BOT_USERNAME}")
    await websocket.send(f"JOIN #{CHANNEL_NAME}")

    await _keep_alive(websocket)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
