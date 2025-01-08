from services.main.utils.caching.redis import redis_session
from core.logger import logger
import os
import json

class SessionDataHandler:
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 36000))

    @staticmethod
    def store_message(session_id: str, client_id: str, role: str, message: str):

        try:
            redis_key = f"chat_history:{session_id}:{client_id}"
            structured_message = json.dumps({"role": role, "message": message})
            redis_session.rpush(redis_key, structured_message)
            redis_session.expire(redis_key, SessionDataHandler.SESSION_TIMEOUT)
        except Exception as e:
            logger.debug(f"Error storing message: {e}")

    @staticmethod
    def store_current_plan(session_id: str, client_id: str, plan_data: dict):

        try:
            redis_key = f"current_plan:{session_id}:{client_id}"
            redis_session.set(redis_key, json.dumps(plan_data))
            redis_session.expire(redis_key, SessionDataHandler.SESSION_TIMEOUT)
        except Exception as e:
            logger.debug(f"Error storing current plan: {e}")

    @staticmethod
    def get_chat_history(session_id: str, client_id: str):

        try:
            chat_key = f"chat_history:{session_id}:{client_id}"
            raw_history = redis_session.lrange(chat_key, 0, -1)
            chat_history = [json.loads(msg) for msg in raw_history]

            plan_key = f"current_plan:{session_id}:{client_id}"
            plan_data = redis_session.get(plan_key)
            current_plan = json.loads(plan_data) if plan_data else None

            return {
                "chat_history": chat_history,
                "current_plan": current_plan
            }
        except Exception as e:
            logger.debug(f"Error retrieving chat history or current plan: {e}")
            return {"chat_history": [], "current_plan": None}



class TFDocsCache:
    def store_docs(resource: str, doc: str):
        try:
            if doc:
                redis_session.set(resource, doc, ex=86400)
        except Exception as e:
            logger.debug(f"Error storing docs: {e}")

    def get_docs(resource: str):
        try:
            return redis_session.get(resource)
        except Exception as e:
            logger.debug(f"Error retrieving docs: {e}")
            return None