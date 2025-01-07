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
        terraform_docs: str,
    ) -> str:
        """
        Prepare the prompt for Docker deployment
        """

        PROMPT_TO_GENERATE = docker_prompt.format(
            project_details, user_preferences, prompt, chat_history, terraform_docs
        )

        return PROMPT_TO_GENERATE


    def prepare_conversation_prompt(self, request: MessageRequest, chat_history: str):
        prompt = f'''
        You are Deplora AI assistant, a chatbot designed to assist users with deployment-related queries.
        Based on the conversation, generate a suitable response, and provide any additional information or context as needed.

         input: {request.message}
         chat history: {chat_history}

         output:
         '''
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
    
    def prepare_client_feedBack_prompt(self, prompt: str, chat_history: dict, project_details: dict, user_preferences: dict, current_plan: dict):
        prompt = f'''
        You are an expert deployment solution architect. Currently, the client has a deployment plan in place. 
        Your task is to classify the best deployment plan for the given project based on its details, user preferences, and specific prompt and the chat history.

        ### Deployment Options:
        1. **Dockerized Deployments (Containerization)**:
        - Suitable for small to medium projects.
        - Benefits include portability, consistency across environments, and simplicity.
        2. **Kubernetes-Orchestrated Deployment**:
        - Best for large-scale projects requiring scalability, microservices orchestration, or advanced features like load balancing and rolling updates.
        3. **AMI/VM Image-Based Deployment**:
        - Ideal for immutable infrastructure, compliance with strict security or performance requirements, or traditional VM-based setups.

        ### Project Data: {project_details}

        ### User Preferences: {user_preferences}

        ### User Prompt: {prompt}

        ### Chat History: {chat_history}

        ### Current Plan: {current_plan}

        ### Task:
        Based on the conversation, the project data, user preferences, and user prompt, classify the most suitable deployment plan from the options above. Explain your reasoning clearly and concisely.

        ### Output Format (JSON):
        {{
        "Deployment Plan": "<Best deployment method>",
        "Reasoning": "Based on your prompt and preferences, this plan is most suitable because <explain reasoning>."
        }}

        STRICTLY follow the output format provided. DO NOT output anything else.'''
        return prompt
