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


class PlanGeneratorService:

    def __init__(self):
        self.llm_service = LLMService()
        self.prompt_manager_service = PromptManagerService()
        self.file_parser = FileParser()
        self.validator_service = ValidatorService()
        self.terraform_doc_scraper = TerraformDocScraper()

        self.MAX_VALIDATION_ITERATIONS = 1
        self.PLAN_GENERATION_PLATFORM = "gemini"

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
            # Initialize the browser asynchronously
            initialize_browser_task = asyncio.create_task(
                self.terraform_doc_scraper.initialize_browser()
            )

            # Get deployment recommendation in the form of a JSON
            # { "Deployment Plan": "",  "Reasoning": ""}
            classification_prompt = (
                await self.prompt_manager_service.prepare_classification_prompt(
                    user_preferences, project_details, prompt
                )
            )
            deployment_recommendation = await self.llm_service.llm_request(
                prompt=classification_prompt
            )

            deployment_recommendation = self.file_parser.parse_json(
                deployment_recommendation
            )

            deployment_strategy = deployment_recommendation["Deployment Plan"]
            logger.info(f"Deployment strategy: {deployment_strategy}")

            # Wait for the browser to initialize
            await initialize_browser_task

            # Identify resources
            identified_resources, terraform_docs = await self._identify_resources(
                deployment_strategy,
                user_preferences,
                project_details,
                chat_history,
                prompt,
            )
            logger.info(f"Identified resources: {identified_resources}")

            # logger.info(f"Terraform docs: {terraform_docs}")

            # Generate initial deployment solution
            terraform_docs = ""
            generation_prompt = self._get_strategy_prompt(
                deployment_strategy,
                user_preferences,
                project_details,
                chat_history,
                prompt,
                terraform_docs,
            )
            deployment_solution = await self.llm_service.llm_request(
                prompt=generation_prompt, platform=self.PLAN_GENERATION_PLATFORM
            )
            logger.info(f"Deployment recommendation: {deployment_recommendation}")
            logger.info(f"Deployment solution: {deployment_solution}")

            parsed_files, parsed_file_content = self.file_parser.parse(
                deployment_solution
            )

            # Validate and fix files
            # parsed_files = await self._validate_and_fix_files(
            #     parsed_files, parsed_file_content
            # )

            return (deployment_recommendation, deployment_solution, parsed_files)

        except Exception as e:
            logger.error(f"Error occurred: {traceback.print_exc()}")
            raise e

    def _get_strategy_prompt(
        self, strategy, preferences, details, history, prompt, terraform_docs
    ):
        refine = False

        if history["current_plan"]:
            refine = True

        if DeploymentOptions.DOCKERIZED_DEPLOYMENT.value in strategy:
            if refine:
                return self.prompt_manager_service.prepare_docker_refine_prompt(
                    preferences, details, history, prompt, history["current_plan"]
                )
            else:
                return self.prompt_manager_service.prepare_docker_prompt(
                    preferences, details, history, prompt, terraform_docs
                )
        elif DeploymentOptions.KUBERNETES_DEPLOYMENT.value in strategy:
            # TODO: Add Kubernetes-specific logic
            return ""
        elif DeploymentOptions.VM_DEPLOYMENT.value in strategy:
            # TODO: Add VM-specific logic
            return ""
        else:
            raise ValueError(f"Unsupported deployment strategy: {strategy}")

    async def _validate_and_fix_files(self, parsed_files, file_content) -> list:
        parsed_files_map = {file["path"]: file for file in parsed_files}
        for i in range(self.MAX_VALIDATION_ITERATIONS):
            feedback = await self.validator_service.check_for_hardcoded_values(
                file_content
            )
            if "no issues identified" in feedback.lower():
                logger.info("Validation successful.")
                break
            logger.info("Validation failed. Attempting to fix issues.")
            fix_prompt = self.prompt_manager_service.prepare_fix_identified_validation_issues_prompt(
                file_content, feedback
            )
            updated_solution = await self.llm_service.llm_request(
                prompt=fix_prompt, platform=self.PLAN_GENERATION_PLATFORM
            )
            parsed_files, file_content = self.file_parser.parse(updated_solution)
            parsed_files_map.update({file["path"]: file for file in parsed_files})
        else:
            logger.error("Validation failed after maximum iterations.")
        return list(parsed_files_map.values())

    async def _fetch_resource_with_doc(self, resource):
        """
        Fetch the Terraform resource documentation using TerraformDocScraper.
        """
        try:
            # Await the async fetch_definition method directly
            content = await self.terraform_doc_scraper.fetch_definition(resource)
            return {"resourceName": resource, "doc": content}
        except Exception as e:
            logger.error(
                f"Error fetching resource doc for {resource}: {traceback.format_exc()}"
            )
            return {"resourceName": resource, "doc": None}

    async def _identify_resources(
        self,
        deployment_strategy,
        user_preferences,
        project_details,
        chat_history,
        prompt,
    ):
        """
        Identify resources and fetch their Terraform documentation.
        """
        try:
            resourcing_prompt = (
                self.prompt_manager_service.prepare_identify_resources_prompt(
                    deployment_strategy,
                    user_preferences,
                    project_details,
                    chat_history,
                    prompt,
                )
            )
            # Send prompt to LLM service to identify resources
            response = await self.llm_service.llm_request(prompt=resourcing_prompt)
            logger.info(f"Identified resources response: {response}")
            identified_resources = self.file_parser.parse_json(response)["resources"]
            logger.info(f"Identified resources: {identified_resources}")

        except Exception as e:
            logger.error(f"Error identifying resources: {traceback.format_exc()}")
            identified_resources = []

        # Create a list of tasks to fetch documentation for each resource
        tasks = [
            self._fetch_resource_with_doc(resource) for resource in identified_resources
        ]
        # Wait for all tasks to complete
        terraform_docs = await asyncio.gather(*tasks)

        # Filter out resources without documentation
        terraform_docs = [doc for doc in terraform_docs if doc["doc"] is not None]

        return identified_resources, json.dumps(terraform_docs, indent=4)
