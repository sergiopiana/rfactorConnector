import asyncio
import json
import websockets
import threading

class WebSocketServer:
    def __init__(self, port=8765):
        self.port = port
        self.connected_clients = set()
        self.current_telemetry = {}
        self.loop = None
        self.thread = None

    async def register(self, websocket):
        self.connected_clients.add(websocket)
        print(f"New Client Connected. Total: {len(self.connected_clients)}")
        try:
            await websocket.wait_closed()
        finally:
            self.connected_clients.remove(websocket)
            print(f"Client Disconnected. Total: {len(self.connected_clients)}")

    async def broadcast_loop(self):
        while True:
            if self.connected_clients and self.current_telemetry:
                message = json.dumps(self.current_telemetry)
                # Create tasks for sending to all clients
                tasks = [asyncio.create_task(ws.send(message)) for ws in self.connected_clients]
                if tasks:
                    await asyncio.wait(tasks)
            await asyncio.sleep(0.016) # ~60 Hz

    async def start(self):
        async with websockets.serve(self.register, "0.0.0.0", self.port):
            print(f"WebSocket Server running on ws://0.0.0.0:{self.port}")
            await self.broadcast_loop()

    def _run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start())

    def start_server(self):
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def broadcast(self, telemetry_data: dict):
        self.current_telemetry = telemetry_data
