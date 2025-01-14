from services.main.excecutor.JenkinsManager import JenkinsManager
from services.main.utils.caching.redis_service import SessionDataHandler

jenkins = JenkinsManager()

async def excecute_pipeline(session_id: str):
    chat_history = SessionDataHandler.get_session_data(session_id)
    
    jenkins.create_folder(chat_history["organization_id"])
    jenkins.create_local_pipeline(    chat_history["organization_id"], chat_history["session_id"], chat_history["repo_path"])
    
    jenkins.trigger_pipeline_build(chat_history["organization_id"], chat_history["session_id"])
    return chat_history
    
    
    