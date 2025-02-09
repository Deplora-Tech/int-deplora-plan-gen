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
        jenkins.create_folder(chat_history["organization_id"])
        jenkins.create_local_pipeline(
            chat_history["organization_id"],
            chat_history["session_id"],
            chat_history["repo_path"],
        )

        build_info = ""

        while not build_info:
            try:
                build_info = jenkins.trigger_pipeline_build(
                    chat_history["organization_id"], chat_history["session_id"]
                )
            except Exception as e:
                pass

        build_id = build_info["id"]
        logger.info(f"Build ID: {build_id}")

        x = 0
        while build_info["building"]:
            stages_info = jenkins.get_stages_info(
                chat_history["organization_id"], chat_history["session_id"], build_id
            )
            logger.info(f"Stages Info: {stages_info}")

            build_info["stages"] = stages_info
            print(build_info)

            await communication_service.publisher(
                chat_history["session_id"],
                ExcecutionStatus.INITIALIZE.value,
                build_info,
            )

            await asyncio.sleep(1)
            x += 1
            if x >= 100:
                break

    except Exception as e:
        logger.error(f"Error excecution pipeline: {traceback.format_exc()}")
        await communication_service.publisher(
            chat_history["session_id"], ExcecutionStatus.FAILED.value, {"error": str(e)}
        )
