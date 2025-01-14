from services.main.excecutor.JenkinsManager import JenkinsManager
from services.main.utils.caching.redis_service import SessionDataHandler

jenkins = JenkinsManager()

async def excecute_pipeline(session_id: str):
    chat_history = await SessionDataHandler.get_session_data(session_id)
    clone_dir = chat_history["repo_path"]
    