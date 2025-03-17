import json

from services.main.workers.llm_worker import LLMService
from services.main.utils.prompts.service import PromptManagerService
from services.main.enums import DeploymentOptions
from services.main.management.planGenerator.FileParser import FileParser

from services.main.management.planGenerator.TerraformDocScraper import (
    TerraformDocScraper,
)
from services.main.management.validationManager.service import ValidatorService
from core.logger import logger
import asyncio
import concurrent.futures
import traceback
from services.main.management.planGenerator.PlanGenAgent.run import invokeAgent


class PlanGeneratorService:

    def __init__(self):
        self.llm_service = LLMService()
        self.prompt_manager_service = PromptManagerService()
        self.file_parser = FileParser()
        self.validator_service = ValidatorService()
        self.terraform_doc_scraper = TerraformDocScraper()

        self.MAX_VALIDATION_ITERATIONS = 0
        self.PLAN_GENERATION_PLATFORM = "gemini"
        self.PLAN_GENERATION_MODEL = "" #"gemini-2.0-flash-thinking-exp-01-21"

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

        try:
            agentFinalState = invokeAgent(user_preferences,project_details, prompt, chat_history)
            
            deployment_recommendation = agentFinalState.deployment_strategy
            deployment_solution = agentFinalState.deployment_solution
            print("deployment_recommendation",deployment_recommendation)
            print("deployment_solution",deployment_solution)

            
            parsed_files, parsed_file_content = self.file_parser.parse(
                deployment_solution
            )
            return (deployment_recommendation, deployment_solution, parsed_files)

        except Exception as e:
            logger.error(f"Error occurred: {traceback.print_exc()}")
            raise e

    