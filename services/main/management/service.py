from core.logger import logger
from services.main.communication.models import MessageRequest
from services.main.communication.service import CommunicationService
from services.main.enums import LoraStatus
from services.main.promptManager.service import PromptManagerService
from services.main.planGenerator.service import PlanGeneratorService
from services.main.repoManager.service import RepoService
from services.main.workers.llm_worker import LLMService

import asyncio, os
from dotenv import load_dotenv


class ManagementService:
    def __init__(self):
        # self.validation_service = ValidatorService(
        #     "C:\\Users\\thamb\\Downloads\\validate"
        # )
        load_dotenv()
        self.repo_service = RepoService(os.getenv("REPO_PATH"))
        self.plan_generator_service = PlanGeneratorService()
        self.llm_service = LLMService()
        self.prompt_manager_service = PromptManagerService()

    async def generate_deployment_plan(
            self,
            prompt: str,
            project_id: str,
            organization_id: str,
            user_id: str,
            chat_history: dict,
            session_id: str,
            communication_service: CommunicationService
    ) -> dict:

        try:
            git_url = "https://github.com/sahiruw/po-server"
            repo_task = self.repo_service.clone_repo(
                repo_url=git_url, branch="main", session_id=session_id
            )
            await communication_service.publisher(user_id, LoraStatus.RETRIEVING_USER_PREFERENCES.value)

            preferences_task = self.retrieve_preferences(
                prompt=prompt,
                project_id=project_id,
                organization_id=organization_id,
                user_id=user_id,
                chat_history=chat_history,
            )

            await communication_service.publisher(user_id, LoraStatus.RETRIEVING_PROJECT_DETAILS.value)
            project_details_task = self.retrieve_project_details(project_id)

            repo, user_preferences, project_details = await asyncio.gather(
                repo_task, preferences_task, project_details_task
            )

            await communication_service.publisher(user_id, LoraStatus.GENERATING_DEPLOYMENT_PLAN.value)

            deployment_recommendation, deployment_solution, parsed_files = (
                await self.plan_generator_service.generate_deployment_plan(
                    prompt=prompt,
                    user_preferences=user_preferences,
                    project_details=project_details,
                    chat_history=chat_history,
                )
            )
            
            logger.info(f"Files to be committed: {len(parsed_files)}")
            await communication_service.publisher(user_id, LoraStatus.GATHERING_DATA.value)
            
            await self.repo_service.create_files_in_repo(repo, parsed_files)

            logger.info("Files committed successfully.")
            folder_structure, file_contents = self.repo_service.get_folder_and_content(parsed_files)
            return {
                "status": "success",
                "response": deployment_recommendation["Deployment Plan"],
                "folder_structure": folder_structure,
                "file_contents": file_contents  # Add file contents in response
            }
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            await communication_service.publisher(user_id, LoraStatus.FAILED.value)
            raise e


    async def process_conversation(self, request: MessageRequest, chat_history: str) -> dict:
        prompt = self.prompt_manager_service.prepare_conversation_prompt(request, chat_history)
        res =  await self.llm_service.llm_request(prompt)
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
        preferences = {'positive_preferences': [['CloudProvider', 'Azure', 0.81809013001114, 'High'], ['ObjectStorageService', 'S3', 0.6786340000000001, 'Low'], ['ComputeService', 'Lambda', 0.6722666666666667, 'Low'], ['IdentityAndAccessManagementService', 'IAM', 0.6571, 'Low'], ['DatabaseService', 'RDS', 0.649, 'Low'], ['ContainerOrchestrationPlatform', 'ECS', 0.64, 'Low'], ['OtherService', 'VPC', 0.64, 'Low'], ['MessageQueueService', 'Pub/Sub', 0.63, 'Low'], ['NoSQLDatabaseService', 'Firestore', 0.63, 'Low'], ['ContentDeliveryNetwork', 'CloudFront', 0.626, 'Low'], ['MonitoringService', 'CloudWatch', 0.61, 'Low']], 'negative_preferences': []}

        # await asyncio.sleep(2)
        return preferences

    async def retrieve_project_details(self, project_id: str) -> dict:
        logger.debug("Retrieving project details...")

        project_data = {
            "application": {
                "name": "React Application",
                "type": ["Web Application", "ReactJS", "React"],
                "description": "A Simple ReactJS Project",
                "dependencies": [
                    {
                        "name": "React",
                        "version": "x.x.x",
                    },
                    "react-router-dom",
                    "react-bootstrap",
                    "axios",
                ],
                "language": ["JavaScript"],
                "framework": ["ReactJS"],
                "architecture": ["Single-page application", "Client-Server"],
            },
            "environment": {"runtime": ["Node.js"]},
        }

        # await asyncio.sleep(3)
        return project_data
