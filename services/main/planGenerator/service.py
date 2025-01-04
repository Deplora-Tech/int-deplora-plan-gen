from services.main.workers.llm_worker import LLMService
from services.main.promptManager.service import PromptManagerService
from services.main.enums import DeploymentOptions
from core.logger import logger
import json


class PlanGeneratorService:

    def __init__(self):
        self.llm_service = LLMService()
        self.prompt_manager_service = PromptManagerService(self.llm_service)

    async def generate_deployment_plan(
        self,
        prompt: str,
        user_preferences: dict,
        project_details: dict,
        chat_history: dict,
    ) -> dict:
        """
        Generate a deployment plan based on the request
        1. Prepare the prompt
        2. Call Prompt Manager Service
        """

        classification_prompt = (
            await self.prompt_manager_service.prepare_classification_prompt(
                user_preferences, project_details, prompt
            )
        )

        # { "Deployment Plan": "",  "Reasoning": ""}
        deployment_recommendation = await self.llm_service.llm_request(
            classification_prompt
        )

        deployment_recommendation = json.loads(deployment_recommendation)

        # deployment_recommendation = { "Deployment Plan": "Dockerized Deployments (Containerization)", "Reasoning": "Based on your prompt and preferences, this plan is most suitable because it aligns with your specified technology and preference for Docker, offering the benefits of portability and simplicity." }

        deployment_strategy = deployment_recommendation["Deployment Plan"]

        logger.info(f"Deployment strategy: {deployment_strategy}")

        if deployment_strategy == DeploymentOptions.KUBERNETES_DEPLOYMENT.value:
            generation_prompt = ""
            pass  # TODO

        elif deployment_strategy == DeploymentOptions.VM_DEPLOYMENT.value:
            generation_prompt = ""
            pass  # TODO

        elif deployment_strategy == DeploymentOptions.DOCKERIZED_DEPLOYMENT.value:
            generation_prompt = self.prompt_manager_service.prepare_docker_prompt(
                user_preferences, project_details, chat_history, prompt
            )

        else:
            return {}  # TODO
        print(generation_prompt)
        deployment_solution = await self.llm_service.llm_request(generation_prompt)
        
        return deployment_recommendation, deployment_solution
