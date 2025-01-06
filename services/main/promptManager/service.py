from services.main.promptManager.promptsv001 import (
    classification_prompt,
    docker_prompt,
    identify_resources_prompt,
)
from services.main.promptManager.promptsv001 import (
    validate_for_hardcoded_values_prompt,
    fix_identified_validation_issues_prompt,
)
from services.main.communication.models import MessageRequest
from services.main.workers.llm_worker import LLMService


class PromptManagerService:
    def __init__(self):
        self.llm_service = LLMService()

    async def prepare_classification_prompt(
        self,
        user_preferences: dict,
        project_details: dict,
        prompt: str,
    ) -> str:
        """
        Prepare the initial prompt for the user
        """

        PROMPT_TO_IDENTIFY_DEPLOYMENT_OPTION = classification_prompt.format(
            user_preferences, project_details, prompt
        )

        return PROMPT_TO_IDENTIFY_DEPLOYMENT_OPTION

    def prepare_docker_prompt(
        self,
        user_preferences: dict,
        project_details: dict,
        chat_history: dict,
        prompt: str,
    ) -> str:
        """
        Prepare the prompt for Docker deployment
        """

        PROMPT_TO_GENERATE = docker_prompt.format(
            project_details, user_preferences, prompt, chat_history
        )

        return PROMPT_TO_GENERATE

    def prepare_conversation_prompt(self, request: MessageRequest):
        prompt = f"""
         You are Deplora AI assistant, a chatbot designed to assist users with deployment-related queries.
         Based on the conversation, generate a suitable response, and provide any additional information or context as needed.

         input: {request.message}
         chat history: {request.chat_history}

         output:
         """
        return prompt

    def prepare_validate_for_hardcoded_values_prompt(self, file_str: str):
        prompt = validate_for_hardcoded_values_prompt.format(file_str)
        return prompt

    def prepare_fix_identified_validation_issues_prompt(
        self, file_str: str, issues: str
    ):
        prompt = fix_identified_validation_issues_prompt.format(file_str, issues)
        return prompt

    def prepare_identify_resources_prompt(
        self,
        deployment_strategy: str,
        user_preferences: dict,
        project_details: dict,
        chat_history: dict,
        prompt: str,
    ):
        prompt = identify_resources_prompt.format(
            deployment_strategy, project_details, user_preferences, prompt, chat_history
        )

        return prompt
