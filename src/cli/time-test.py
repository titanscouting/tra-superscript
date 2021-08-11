import asyncio
import datetime
import random
import websockets

async def time(websocket, path):
	print(path)
	i = 0
	while True:
		#now = datetime.datetime.utcnow().isoformat() + "Z"
		#await websocket.send(now)
		#await asyncio.sleep(random.random() * 3)
		i += 1
		await websocket.send(str(i))
		await asyncio.sleep(1)

start_server = websockets.serve(time, "127.0.0.1", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()