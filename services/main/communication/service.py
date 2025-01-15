from fastapi.websockets import WebSocket
from typing import Dict
import json
import asyncio  # For simulating typing indicators or delays

from core.logger import logger


class CommunicationService:
    def __init__(self):
        # Dictionary to map client IDs to WebSocket connections
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Establish a connection and map it to the client ID."""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """Remove a client from active connections."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def publisher(
        self, client_id: str, status: str, data: dict = {}
    ):  ## publisher for use anywhere in the application
        websocket = self.active_connections.get(client_id)
        logger.debug(f"status: {status}, clientId: {client_id}, websocket: {websocket}")
        if websocket:
            try:
                if isinstance(data, dict):
                    data = json.dumps(data)

                message = json.dumps({"status": status, "data": data or {}})

                await websocket.send_text(message)
            except Exception as e:
                print(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
        else:
            print(f"Client {client_id} not connected.")
