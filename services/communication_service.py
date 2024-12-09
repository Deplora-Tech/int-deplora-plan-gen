from fastapi.websockets import WebSocket

class CommunicationService:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def process_message(self, message: str):
        # Logic for processing client messages
        if message == "start":
            return "Initiating deployment plan generation..."
        return f"Received: {message}"
