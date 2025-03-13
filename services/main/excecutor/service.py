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
    

        jenkins.create_folder(chat_history["organization_id"], chat_history["repo_path"])
        jenkins.create_local_pipeline(
            chat_history["organization_id"],
            chat_history["session_id"],
            chat_history["repo_path"],
        )

        

        build_id = jenkins.trigger_pipeline_build(
                    chat_history["organization_id"], chat_history["session_id"]
                )
        logger.info(f"Build ID: {build_id}")
        build_info["id"] = build_id
        await communication_service.publisher(
                chat_history["session_id"],
                ExcecutionStatus.INITIALIZE.value,
                build_info,
            )

        build_info = jenkins.monitor_build_status(
            chat_history["organization_id"],
            chat_history["session_id"],
            build_id,
        )
        
        x = 0
        while build_info["building"]:
            stages_info, is_building = jenkins.get_stages_info(
                chat_history["organization_id"], chat_history["session_id"], build_id
            )

            build_info["stages"] = stages_info
            build_info["building"] = is_building

            for stage in stages_info:
                logs = jenkins.get_logs_for_stage(
                    chat_history["organization_id"],
                    chat_history["session_id"],
                    build_id,
                    stage["id"],
                )
                stage["logs"] = logs.split("\n")


            await communication_service.publisher(
                chat_history["session_id"],
                ExcecutionStatus.PROCESSING.value,
                build_info,
            )

            # await asyncio.sleep(1)
            x += 1
            if x >= 10000:
                logger.info("Breaking")
                break

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