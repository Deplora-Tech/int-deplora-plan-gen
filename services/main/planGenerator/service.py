import json
from typing import Dict, Any, Tuple, List

from anthropic.types import TextBlock, ToolUseBlock

from services.main.workers.llm_worker import LLMService
from services.main.promptManager.service import PromptManagerService
from services.main.enums import DeploymentOptions
from services.main.planGenerator.FileParser import FileParser
from services.main.validationManager.service import ValidatorService
from core.logger import logger


class PlanGeneratorService:

    def __init__(self):
        self.llm_service = LLMService()
        self.prompt_manager_service = PromptManagerService()
        self.file_parser = FileParser()
        self.validator_service = ValidatorService()

        self.MAX_VALIDATION_ITERATIONS = 1

    async def generate_deployment_plan(
        self,
        prompt: str,
        user_preferences: dict,
        project_details: dict,
        chat_history: dict,
    ) -> dict[Any, Any] | tuple[Any, Any, list[str], dict[str, str]]:
        logger.info("Generating deployment plan.")
        """
        Generate a deployment plan based on the request
        1. Prepare the prompt
        2. Call Prompt Manager Service
        """
        """
        if chat_history contain a current plan then based on the prompt, generate a suitable response, 
        and provide any additional information or context as needed. with enhanced plan
        """
        if chat_history["current_plan"]:
            classification_prompt = await self.prompt_manager_service.prepare_client_feedback_prompt(
                prompt, chat_history["chat_history"], project_details, user_preferences, chat_history["current_plan"]
            )
        else:
            classification_prompt = (
                await self.prompt_manager_service.prepare_classification_prompt(
                    user_preferences, project_details, prompt
                )
            )

        logger.info(f"Classification prompt: {classification_prompt}")

        deployment_recommendation = await self.llm_service.llm_request(
            prompt=classification_prompt
        )
        logger.info(f"Deployment recommendation: {json.loads(deployment_recommendation)}")

        deployment_recommendation = json.loads(deployment_recommendation)

        deployment_strategy = deployment_recommendation["Deployment Plan"]

        logger.info(f"Deployment strategy: {deployment_strategy}")

        resourcing_prompt = (
            self.prompt_manager_service.prepare_identify_resources_prompt(
                deployment_strategy,
                user_preferences,
                project_details,
                chat_history,
                prompt,
            )
        )
        identified_resources = await self.llm_service.llm_request(
            prompt=resourcing_prompt
        )

        logger.info(f"Identified resources: {identified_resources}")

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

        deployment_solution = await self.llm_service.llm_request(
            prompt=generation_prompt, platform="deepseek"
        )

        logger.info(f"Deployment recommendation: {deployment_recommendation}")
        logger.info(f"Deployment solution: {deployment_solution}")

        parsed_files, parsed_file_content = self.file_parser.parse(deployment_solution)

        print("Parsed files: ")
        print("\n\n".join(parsed_file_content))

        parsed_files_dict = {}
        for file in parsed_files:
            parsed_files_dict[file["path"]] = file

        validation_feedback = await self.validator_service.check_for_hardcoded_values(parsed_file_content)

        logger.info("Received validation feedback: ")

        for i in range(self.MAX_VALIDATION_ITERATIONS):
            if not "no issues identified" in validation_feedback.lower():
                logger.info("Failed validation. Fixing identified issues.")
                validation_issues_fixing_prompt = self.prompt_manager_service.prepare_fix_identified_validation_issues_prompt(
                    parsed_file_content, validation_feedback
                )
                deployment_solution = await self.llm_service.llm_request(
                    prompt=validation_issues_fixing_prompt, platform="deepseek"
                )
                parsed_files, parsed_file_content = self.file_parser.parse(
                    deployment_solution
                )

                for file in parsed_files:
                    parsed_files_dict[file["path"]] = file

                validation_feedback = (
                    await self.validator_service.check_for_hardcoded_values(
                        parsed_file_content
                    )
                )

            else:
                logger.info("Validation successful.")
                break

        else:
            logger.error("Validation failed after maximum iterations.")
            parsed_files = list(parsed_files_dict.values())

            return (
                deployment_recommendation,
                deployment_solution,
                parsed_files,
                parsed_file_content,
            )
