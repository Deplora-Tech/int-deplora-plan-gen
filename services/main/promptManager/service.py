from services.main.promptManager.prompts import classification_prompt, docker_prompt
from services.main.communication.models import MessageRequest

class PromptManagerService:
    def __init__(self, llm_service):
        self.llm_service = llm_service

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
        prompt = f'''
         You are Deplora AI assistant, a chatbot designed to assist users with deployment-related queries.
         Based on the conversation, generate a suitable response, and provide any additional information or context as needed.

         input: {request.message}
         chat history: {request.chat_history}

         output:
         '''
        return prompt
