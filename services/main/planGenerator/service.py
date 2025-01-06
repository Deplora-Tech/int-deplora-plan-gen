import json

from services.main.workers.llm_worker import LLMService
from services.main.promptManager.service import PromptManagerService
from services.main.enums import DeploymentOptions
from services.main.planGenerator.FileParser import FileParser

from services.main.planGenerator.TerraformDocScraper import TerraformDocScraper
from services.main.validationManager.service import ValidatorService
from core.logger import logger
import asyncio


class PlanGeneratorService:

    def __init__(self):
        self.llm_service = LLMService()
        self.prompt_manager_service = PromptManagerService()
        self.file_parser = FileParser()
        self.validator_service = ValidatorService()
        self.terraform_doc_scraper = TerraformDocScraper()

        self.MAX_VALIDATION_ITERATIONS = 1
        self.PLAN_GENERATION_PLATFORM = "deepseek"

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
        deployment_recommendation = json.loads(deployment_recommendation)
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
        generation_prompt = self._get_strategy_prompt(
            deployment_strategy, user_preferences, project_details, chat_history, prompt, terraform_docs
        )
        deployment_solution = await self.llm_service.llm_request(
            prompt=generation_prompt, platform=self.PLAN_GENERATION_PLATFORM
        )
        logger.info(f"Deployment recommendation: {deployment_recommendation}")
        logger.info(f"Deployment solution: {deployment_solution}")

        parsed_files, parsed_file_content = self.file_parser.parse(deployment_solution)

        print("Parsed files: ")
        print("\n\n".join(parsed_file_content))

        # Validate and fix files
        parsed_files = await self._validate_and_fix_files(
            parsed_files, parsed_file_content
        )

        return (deployment_recommendation, deployment_solution, parsed_files)

    def _get_strategy_prompt(self, strategy, preferences, details, history, prompt, terraform_docs):

        if strategy == DeploymentOptions.DOCKERIZED_DEPLOYMENT.value:
            return self.prompt_manager_service.prepare_docker_prompt(
                preferences, details, history, prompt, terraform_docs
            )
        elif strategy == DeploymentOptions.KUBERNETES_DEPLOYMENT.value:
            # TODO: Add Kubernetes-specific logic
            return ""
        elif strategy == DeploymentOptions.VM_DEPLOYMENT.value:
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
        doc = await self.terraform_doc_scraper.fetch_definition(
            resource.replace("aws_", "")
        )
        return {"resourceName": resource, "doc": doc}

    async def _identify_resources(
        self,
        deployment_strategy,
        user_preferences,
        project_details,
        chat_history,
        prompt,
    ):
        resourcing_prompt = (
            self.prompt_manager_service.prepare_identify_resources_prompt(
                deployment_strategy,
                user_preferences,
                project_details,
                chat_history,
                prompt,
            )
        )
        response = await self.llm_service.llm_request(prompt=resourcing_prompt)
        identified_resources = json.loads(response)["resources"]

        terraform_docs = await asyncio.gather(
            *(
                self._fetch_resource_with_doc(resource)
                for resource in identified_resources
            )
        )
        
        terraform_docs = [doc for doc in terraform_docs if doc["doc"] is not None]

        return identified_resources, json.dumps(terraform_docs, indent=4)
