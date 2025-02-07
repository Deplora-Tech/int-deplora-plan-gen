from fastapi.websockets import WebSocket
from typing import Dict
import json
from core.logger import logger

class CommunicationService:
    _instances: Dict[str, "CommunicationService"] = {} 

    def __new__(cls, name: str = "CommunicationService", *args, **kwargs):
        if name not in cls._instances:
            cls._instances[name] = super(CommunicationService, cls).__new__(cls, *args, **kwargs)
        return cls._instances[name]

    def __init__(self, name: str = "CommunicationService"):
        if not hasattr(self, "active_connections"):
            # Dictionary to map client IDs to WebSocket connections
            self.active_connections: Dict[str, WebSocket] = {}
            self.name = name

    async def connect(self, websocket: WebSocket, client_id: str):
        """Establish a connection and map it to the client ID."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected to {self.name}.")

    def disconnect(self, client_id: str):
        """Remove a client from active connections."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected from {self.name}.")
        else:
            logger.info(f"Client {client_id} not found to disconnect in {self.name}.")

    async def publisher(self, client_id: str, status: str, data: dict = {}):
        """Publisher for use anywhere in the application."""
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
            print(self.active_connections)
            print(f"Client {client_id} not connected.")

