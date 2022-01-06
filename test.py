import asyncio
from websockets import connect

BOT_USERNAME = ''
CHANNEL_NAME = ''
OAUTH_TOKEN = ''

async def _keep_alive(websocket):
    print('keeping alive.')
    try:
        while True:
            print(await websocket.recv())
    except KeyboardInterrupt:
        pass
    finally:
        await websocket.close()
        await websocket.wait_closed()

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
