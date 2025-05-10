from services.main.excecutor.JenkinsManager import JenkinsManager
from services.main.utils.caching.redis_service import SessionDataHandler
from services.main.communication.service import CommunicationService
from core.logger import logger
from services.main.enums import ExcecutionStatus
import traceback, asyncio

jenkins = JenkinsManager()
communication_service = CommunicationService("PipelineService")


async def excecute_pipeline(session_id: str):
    try:
        logger.info(f"Excecution pipeline for session: {session_id}")
        chat_history = SessionDataHandler.get_session_data(session_id)
        logger.info(f"Path: {chat_history['repo_path']}")

        # To provide the initial build info
        stages = jenkins.list_stages(chat_history["repo_path"])
        build_info = {"building": True, "stages": stages}

        await communication_service.publisher(
                chat_history["session_id"],
                ExcecutionStatus.INITIALIZE.value,
                build_info,
            )
    

        # CREATE ORGANIZATION FOLDER
        jenkins.create_org_folder(chat_history["organization_id"])

        # CREATE REPO FOLDER
        jenkins.create_project_folder(
            chat_history["organization_id"],
            chat_history["session_id"],
            chat_history["repo_path"],
        )

        jenkins.create_local_pipeline(
            folder_name=f"{chat_history['organization_id']}/job/{chat_history['session_id']}",
            pipeline_name=chat_history["session_id"],
            local_directory_path=chat_history["repo_path"],
        )

        

        build_id = jenkins.trigger_pipeline_build(
                    folder_name=f"{chat_history["organization_id"]}/job/{chat_history["session_id"]}",
                    pipeline_name=chat_history["session_id"],
                )
        logger.info(f"Build ID: {build_id}")
        build_info["id"] = build_id
        await communication_service.publisher(
                chat_history["session_id"],
                ExcecutionStatus.INITIALIZE.value,
                build_info,
            )

        return build_id
        
    except Exception as e:
        logger.error(f"Error excecution pipeline: {traceback.format_exc()}")
        await communication_service.publisher(
            chat_history["session_id"], ExcecutionStatus.FAILED.value, {"error": str(e)}
        )


async def abort_pipeline(session_id: str, build_id: str):
    try:
        chat_history = SessionDataHandler.get_session_data(session_id)
        jenkins.stop_pipeline_build(chat_history["organization_id"], chat_history["session_id"], build_id)
        await communication_service.publisher(
            chat_history["session_id"], ExcecutionStatus.ABORTED.value, {"message": "Pipeline aborted"}
        )

    except Exception as e:
        logger.error(f"Error aborting pipeline: {traceback.format_exc()}")
        await communication_service.publisher(
            chat_history["session_id"], ExcecutionStatus.FAILED.value, {"error": str(e)}
        )


async def get_status(session_id: str, build_id: str):
    chat_history = SessionDataHandler.get_session_data(session_id)
    stages_info, is_building = jenkins.get_stages_info(
        folder_name=f"{chat_history['organization_id']}/job/{chat_history['session_id']}",
        pipeline_name=chat_history["session_id"],
        build_id=build_id,

    )


    build_info = {}
    
    build_info["stages"] = stages_info
    build_info["building"] = is_building

    for stage in stages_info:
        logs = jenkins.get_logs_for_stage(
            folder_name=f"{chat_history['organization_id']}/job/{chat_history['session_id']}",
            pipeline_name=chat_history["session_id"],
            build_id=build_id,
            stage_id=stage["id"],
        )
        stage["logs"] = logs.split("\n")


    await communication_service.publisher(
        chat_history["session_id"],
        ExcecutionStatus.PROCESSING.value,
        build_info,
    )

    return build_info

