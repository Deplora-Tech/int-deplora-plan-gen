from core.logger import logger
from services.main.analyzer.api import get_generated_template
from services.main.communication.models import MessageRequest, FileChangeRequest
from services.main.communication.service import CommunicationService
from services.main.enums import LoraStatus
from services.main.utils.prompts.service import PromptManagerService
from services.main.management.planGenerator.service import PlanGeneratorService
from services.main.management.planRefiner.service import PlanRefinerService
from services.main.management.repoManager.service import RepoService
from services.main.workers.llm_worker import LLMService
from services.main.utils.caching.redis_service import SessionDataHandler

from services.main.communication.models import GitRepo

import asyncio, os
import traceback
from dotenv import load_dotenv


class ManagementService:
    def __init__(self):
        # self.validation_service = ValidatorService(
        #     "C:\\Users\\thamb\\Downloads\\validate"
        # )
        load_dotenv()
        self.repo_service = RepoService(os.getenv("REPO_PATH"))
        self.plan_generator_service = PlanGeneratorService()
        self.plan_refiner_service = PlanRefinerService()
        self.llm_service = LLMService()
        self.prompt_manager_service = PromptManagerService()
    

    async def refine_deployment_plan(
            self,
            session_id: str,
            prompt: str,
    ) -> dict:
        try:
            session  = SessionDataHandler.get_session_data(session_id)
            current_files = session["current_plan"]
            new_files, changed_files_objs = await self.plan_refiner_service.run_change_agent(
                prompt=prompt,
                current_files=current_files
            )
            SessionDataHandler.store_current_plan(session_id, new_files)


            await self.repo_service.create_files_in_repo(session["repo_path"], changed_files_objs)

        except Exception as e:
            logger.error(f"Error occurred: {traceback.print_exc()}")

            # raise e

    async def generate_deployment_plan(
        self,
        request: MessageRequest,
        prompt: str,
        project: GitRepo,
        organization_id: str,
        user_id: str,
        chat_history: dict,
        session_id: str,
        communication_service: CommunicationService,
    ) -> dict:

        try:
            project_id = project.id
            repo_task = self.repo_service.clone_repo(
                repo_url=project.repo_url, branch=project.branch, session_id=session_id
            )
            await communication_service.publisher(
                session_id, LoraStatus.RETRIEVING_USER_PREFERENCES.value
            )

            SessionDataHandler.update_message_state_and_data(
                session_id,
                request.mid,
                LoraStatus.RETRIEVING_USER_PREFERENCES.value,
                "",
            )

            preferences_task = self.retrieve_preferences(
                prompt=prompt,
                project_id=project_id,
                organization_id=organization_id,
                user_id=user_id,
                chat_history=chat_history,
            )

            await communication_service.publisher(
                session_id, LoraStatus.RETRIEVING_PROJECT_DETAILS.value
            )

            SessionDataHandler.update_message_state_and_data(
                session_id,
                request.mid,
                LoraStatus.RETRIEVING_PROJECT_DETAILS.value,
                "",
            )
            project_details_task = self.retrieve_project_details(project_id)

            repo_path, user_preferences, project_details = await asyncio.gather(
                repo_task, preferences_task, project_details_task
            )

            await communication_service.publisher(
                session_id, LoraStatus.GENERATING_PLAN.value
            )

            SessionDataHandler.update_message_state_and_data(
                session_id,
                request.mid,
                LoraStatus.GENERATING_PLAN.value,
                "",
            )

            deployment_recommendation, deployment_solution, parsed_files = (
                await self.plan_generator_service.generate_deployment_plan(
                    prompt=prompt,
                    user_preferences=user_preferences,
                    project_details=project_details,
                    chat_history=chat_history,
                )
            )

            logger.info(f"Files to be committed: {len(parsed_files)}")
            await communication_service.publisher(
                session_id, LoraStatus.GATHERING_DATA.value
            )

            SessionDataHandler.update_message_state_and_data(
                session_id,
                request.mid,
                LoraStatus.GATHERING_DATA.value,
                "",
            )

            await self.repo_service.create_files_in_repo(repo_path, parsed_files)

            logger.info("Files committed successfully.")
            folder_structure, file_contents = self.repo_service.get_folder_and_content(
                parsed_files
            )
            return {
                "status": "success",
                "response": "Deployment plan generated successfully.",
                "folder_structure": folder_structure,
                "file_contents": file_contents,  # Add file contents in response
            }
        except Exception as e:
            logger.error(f"Error occurred: {traceback.print_exc()}")
            await communication_service.publisher(session_id, LoraStatus.FAILED.value)

            SessionDataHandler.update_message_state_and_data(
                session_id,
                request.mid,
                LoraStatus.FAILED.value,
                "",
            )
            raise e

    async def process_conversation(
        self, request: MessageRequest, chat_history: str
    ) -> dict:
        prompt = self.prompt_manager_service.prepare_conversation_prompt(
            request, chat_history
        )
        res = await self.llm_service.llm_request(prompt)
        return {"status": "success", "response": res}

    async def retrieve_preferences(
        self,
        prompt: str,
        project_id: str,
        organization_id: str,
        user_id: str,
        chat_history: dict,
    ) -> dict:
        logger.debug("Retrieving user preferences...")
        preferences = {
            "positive_preferences": [
                ["CloudProvider", "AWS", 0.81809013001114, "High"],
                ["ObjectStorageService", "S3", 0.6786340000000001, "Low"],
                ["ComputeService", "Lambda", 0.6722666666666667, "Low"],
                ["IdentityAndAccessManagementService", "IAM", 0.6571, "Low"],
                ["DatabaseService", "RDS", 0.649, "Low"],
                ["ContainerOrchestrationPlatform", "ECS", 0.64, "Low"],
                ["OtherService", "VPC", 0.64, "Low"],
                ["MessageQueueService", "Pub/Sub", 0.63, "Low"],
                ["NoSQLDatabaseService", "Firestore", 0.63, "Low"],
                ["ContentDeliveryNetwork", "CloudFront", 0.626, "Low"],
                ["MonitoringService", "CloudWatch", 0.61, "Low"],
            ],
            "negative_preferences": [],
        }

        # await asyncio.sleep(2)
        logger.info(
            f"User preferences retrieved: {preferences} for project_id: {project_id}"
        )
        return preferences

    async def retrieve_project_details(self, project_id: str) -> dict:
        logger.debug("Retrieving project details...")

        # Await the async call to fetch full document
        project_data = await get_generated_template(project_id)
        print(f"Project data: {project_data} for {project_id}")

        return project_data
    
    
    async def update_file(
        self,
        request: FileChangeRequest,
    ) -> dict:
        try:
            session = SessionDataHandler.get_session_data(request.session_id)
            repo_path = session["repo_path"]
            await self.repo_service.create_files_in_repo(
                repo_path=repo_path,
                file_objects=[
                    {
                        "path": request.file_path,
                        "content": request.file_content,
                    }
                ],
            )


            # update session memory
            current_files = session["current_plan"]
            current_files[request.file_path] = request.file_content
            SessionDataHandler.store_current_plan(request.session_id, current_files)

            return {
                "status": "success",
                "response": "File updated successfully.",
            }
        except Exception as e:
            logger.error(f"Error occurred: {traceback.print_exc()}")
            raise e