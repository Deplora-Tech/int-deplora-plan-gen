from services.main.excecutor.JenkinsManager import JenkinsManager
from services.main.utils.caching.redis_service import SessionDataHandler
from services.main.communication.service import CommunicationService
from services.main.management.planGenerator.FileParser import FileParser
from core.logger import logger
from services.main.enums import ExcecutionStatus
import traceback, asyncio

jenkins = JenkinsManager()
communication_service = CommunicationService("PipelineService")


async def check_env_variables(session_id: str):
    try:
        chat_history = SessionDataHandler.get_session_data(session_id)
        logger.info(f"Checking environment variables for session: {session_id}")

        current_plan = chat_history.get("current_plan", {})

        variables_file = current_plan.get("terraform/variables.tf", "")
        tfvars_file = current_plan.get("terraform/terraform.tfvars", "")

        variables = FileParser.parse_terraform_variables(variables_file)
        tfvars = FileParser.parse_terraform_simple_assignments(tfvars_file)

        for tfvar in tfvars:
            if tfvar in variables:
                variables[tfvar]["default"] = tfvars[tfvar]
        
        return variables, {}


    except Exception as e:
        logger.error(f"Error checking environment variables: {traceback.format_exc()}")
        return False 

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

        # store the build id in the session data
        SessionDataHandler.store_pipeline_data(
            session_id=session_id,
            build_id=build_id,
            data={"stages": [{"name": name} for name in stages], "building": True},
        )

        SessionDataHandler.store_message_user(
            session_id=session_id,
            client_id=chat_history["client_id"],
            role="executor",
            message=build_id,
            variation="pipeline",
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
        jenkins.stop_pipeline_build(
            chat_history["organization_id"], chat_history["session_id"], build_id
        )
        await communication_service.publisher(
            chat_history["session_id"],
            ExcecutionStatus.ABORTED.value,
            {"message": "Pipeline aborted"},
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
    all_stages = jenkins.list_stages(chat_history["repo_path"])
    existing_stages = [s["name"] for s in stages_info]

    
    for stage in stages_info:
        logs = jenkins.get_logs_for_stage(
            folder_name=f"{chat_history['organization_id']}/job/{chat_history['session_id']}",
            pipeline_name=chat_history["session_id"],
            build_id=build_id,
            stage_id=stage["id"],
        )
        stage["logs"] = logs.split("\n")

        # Check if there are any new stages that are not in the existing stages
    # If so, add them to the stages_info with status "PENDING"

    for stage in all_stages:
        if stage not in existing_stages:
            stages_info.append({"name": stage, "status": "PENDING"})

    # check if atleast one stage has logs when building=false
    # there can be cases none of the stages are started but pipeline crached
    # probably due to errors in jenkins file
    if not is_building and not any("logs" in stage for stage in stages_info):
        console_out = jenkins.fetch_console_output(
            folder_name=f"{chat_history['organization_id']}/job/{chat_history['session_id']}",
            pipeline_name=chat_history["session_id"],
            build_id=build_id,
        )
        stages_info[0]["logs"] = console_out.split("\n")
        stages_info[0]["status"] = "FAILED"


    build_info = {}

    build_info["stages"] = stages_info
    build_info["building"] = is_building

    await communication_service.publisher(
        chat_history["session_id"],
        ExcecutionStatus.PROCESSING.value,
        build_info,
    )

    # store the build id in the session data
    SessionDataHandler.store_pipeline_data(
        session_id=session_id, build_id=build_id, data=build_info
    )

    return build_info
