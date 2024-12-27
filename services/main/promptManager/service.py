from services.main.promptManager.prompts import classification_prompt, docker_prompt


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
