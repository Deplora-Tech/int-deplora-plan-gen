from core.logger import logger
from services.main.communication.models import MessageRequest
from services.main.prompt.service import PromptService
from services.main.validation.service import ValidationService
from services.main.workers.llm_worker import LLMService

class ManagementService:
    def __init__(self):
        self.prompt_service = PromptService()
        self.validation_service = ValidationService()
        self.llm_service = LLMService()

    async def generate_deployment_plan(self, request: MessageRequest) :

        if not request.client_id or not request.project_id:
            return {"status": "error", "errors": ["Client ID and Project ID are required."]}

        # Step 1: Prepare the structured prompt
        prepared_prompt = self.prompt_service.prepare_prompt(request)
        logger.debug(prepared_prompt)

        # Step 3: Generate the deployment plan using LLM
        deployment_plan = await self.llm_service.llm_request(prepared_prompt)
        # Step 4: Validate the generated deployment plan
        is_valid, errors = self.validation_service.validate_response(deployment_plan)
        if not is_valid:
            return {"status": "error", "errors": errors}

        # Step 5: Return the final deployment plan
        return {"status": "success", "deployment_plan": deployment_plan}

    async def process_conversation(self, request: MessageRequest) -> dict:
        prompt = self.prompt_service.prepare_conversation_prompt(request)
        return await self.llm_service.llm_request(prompt)


