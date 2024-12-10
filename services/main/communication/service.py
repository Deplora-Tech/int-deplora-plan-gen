from fastapi.websockets import WebSocket
from typing import Dict
import asyncio  # For simulating typing indicators or delays

from core.logger import logger
from services.main.communication.utils import process_initial_prompt, process_conversation_message, process_feedback


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

    async def process_request(self, message: str) -> str:
        try:
            # Parse the incoming message
            print(message)
            if message.startswith("INITIAL_PROMPT:"):
                data = message.replace("INITIAL_PROMPT:", "").strip()
                return await process_initial_prompt(data)
            elif message.startswith("CONVERSATION_MESSAGE:"):
                data = message.replace("CONVERSATION_MESSAGE:", "").strip()
                return await process_conversation_message(data)
            elif message.startswith("FEEDBACK:"):
                data = message.replace("FEEDBACK:", "").strip()
                return await process_feedback(data)
            else:
                return f"ERROR: Unrecognized request."
        except Exception as e:
            return f"ERROR: Failed to process request. {str(e)}"

    async def publisher(self, client_id: str, message: str): ## publisher for use anywhere in the application
        websocket = self.active_connections.get(client_id)
        logger.debug(f"message: {message}, clientId: {client_id}, websocket: {websocket}")
        if websocket:
            try:
                await websocket.send_text(message)
            except Exception as e:
                print(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
        else:
            print(f"Client {client_id} not connected.")
