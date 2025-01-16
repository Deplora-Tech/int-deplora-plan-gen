from services.main.excecutor.JenkinsManager import JenkinsManager
from services.main.utils.caching.redis_service import SessionDataHandler
from services.main.communication.api import CommunicationService
from core.logger import logger
from services.main.enums import ExcecutionStatus

jenkins = JenkinsManager()
communication_service = CommunicationService("PipelineService")
async def excecute_pipeline(session_id: str):
    chat_history = SessionDataHandler.get_session_data(session_id)
    
    jenkins.create_folder(chat_history["organization_id"])
    jenkins.create_local_pipeline(    chat_history["organization_id"], chat_history["session_id"], chat_history["repo_path"])
    
    build_info = jenkins.trigger_pipeline_build(chat_history["organization_id"], chat_history["session_id"])
    build_id = build_info["id"]
    logger.info(f"Build ID: {build_id}")
    
    stages_info = jenkins.get_stages_info(chat_history["organization_id"], chat_history["session_id"], build_id)
    logger.info(f"Stages Info: {stages_info}")
    
    build_info["stages"] = stages_info
    
    await communication_service.publisher(chat_history["session_id"], ExcecutionStatus.INITIALIZE.value, build_info)
    
    return chat_history
    
    
    