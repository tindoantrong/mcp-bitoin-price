import asyncio
import websockets
import subprocess
import logging
import os
import sys
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MCP_PIPE')

async def connect_to_server(uri):
    async with websockets.connect(uri) as websocket:
        process = subprocess.Popen(
            ["python", "bitcoin_price.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            encoding='utf-8',
            text=True
        )
        
        await asyncio.gather(
            pipe_ws_to_process(websocket, process),
            pipe_process_to_ws(process, websocket)
        )

async def pipe_ws_to_process(websocket, process):
    async for message in websocket:
        process.stdin.write(message + '\n')
        process.stdin.flush()

async def pipe_process_to_ws(process, websocket):
    while True:
        data = await asyncio.to_thread(process.stdout.readline)
        if not data:
            break
        await websocket.send(data)

if __name__ == "__main__":
    endpoint = os.environ.get('MCP_ENDPOINT')
    if not endpoint:
        print("Set MCP_ENDPOINT environment variable")
        sys.exit(1)
    asyncio.run(connect_to_server(endpoint))