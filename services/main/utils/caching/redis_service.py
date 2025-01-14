from services.main.utils.caching.redis import redis_session, redis_tfcache
from core.logger import logger
import os
import json


class SessionDataHandler:
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 3600 * 24 * 365))

    @staticmethod
    def store_message(session_id: str, client_id: str, role: str, message: str):
        try:
            redis_key = session_id
            # Fetch the existing session or initialize a new one
            session_data = redis_session.get(redis_key)
            session_object = (
                json.loads(session_data) if session_data else {"client_id": client_id}
            )

            # Update chat history
            chat_history = session_object.get("chat_history", [])
            chat_history.append({"role": role, "message": message})

            session_object["chat_history"] = chat_history

            redis_session.set(redis_key, json.dumps(session_object))
            redis_session.expire(redis_key, SessionDataHandler.SESSION_TIMEOUT)
            logger.debug(f"Message stored in session: {redis_key} - {role}: {message}")
        except Exception as e:
            logger.error(f"Error storing message: {e}")

    @staticmethod
    def store_current_plan(session_id: str, client_id: str, plan_data: dict):
        try:
            redis_key = session_id
            # Fetch the existing session or initialize a new one
            session_data = redis_session.get(redis_key)
            session_object = json.loads(session_data) if session_data else {}

            session_object["current_plan"] = plan_data

            redis_session.set(redis_key, json.dumps(session_object))
            redis_session.expire(redis_key, SessionDataHandler.SESSION_TIMEOUT)
            logger.debug(
                f"Current plan stored for client_id: {client_id} in session: {redis_key}"
            )
        except Exception as e:
            logger.error(f"Error storing current plan: {e}")

    @staticmethod
    def get_session_data(session_id: str):
        try:
            redis_key = session_id
            logger.debug(f"Retrieving session data: {redis_key}")
            session_data = redis_session.get(redis_key)
            if session_data:
                return json.loads(session_data)
            return {}
        except Exception as e:
            logger.error(f"Error retrieving session data: {e}")
            return {}

    @staticmethod
    def get_chat_history(session_id: str):
        try:
            session_data = SessionDataHandler.get_session_data(session_id)

            return {
                "chat_history": session_data.get("chat_history", []),
                "current_plan": session_data.get("current_plan", None),
            }
        except Exception as e:
            logger.error(f"Error retrieving chat history: {e}")
            return {"chat_history": None, "current_plan": None}

    @staticmethod
    def get_client_data(session_id: str, client_id: str):
        try:
            session_data = SessionDataHandler.get_session_data(session_id)
            return session_data.get(client_id, {})
        except Exception as e:
            logger.error(f"Error retrieving client data: {e}")
            return {}
        
    
    @staticmethod
    def update_session_data(session_id: str, data: dict):
        try:
            redis_key = session_id
            # Fetch the existing session or initialize a new one
            session_data = redis_session.get(redis_key)
            session_object = json.loads(session_data) if session_data else {}

            # Update the session data with multiple key-value pairs
            session_object.update(data)
            

            # Store the updated session data back to Redis
            redis_session.set(redis_key, json.dumps(session_object))
            redis_session.expire(redis_key, SessionDataHandler.SESSION_TIMEOUT)

            logger.debug(f"Session data updated for session_id: {session_id}")

        except Exception as e:
            logger.error(f"Error updating session data: {e}")



class TFDocsCache:
    def store_docs(resource: str, doc: str):
        try:
            if doc:
                redis_tfcache.set(resource, doc, ex=86400)
        except Exception as e:
            logger.debug(f"Error storing docs: {e}")

    def get_docs(resource: str):
        try:
            return redis_tfcache.get(resource)
        except Exception as e:
            logger.debug(f"Error retrieving docs: {e}")
            return None
