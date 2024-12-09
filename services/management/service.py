from services.prompt.service import PromptService
from services.validation.service import ValidationService
from workers.llm_worker import send_to_llm

class ManagementService:
    def __init__(self):
        self.prompt_service = PromptService()
        self.validation_service = ValidationService()

    async def generate_deployment_plan(self, request: dict):
        # Step 1: Prepare the prompt
        prompt = self.prompt_service.prepare_prompt(request)

        # Step 2: Validate the prompt
        is_valid, errors = self.validation_service.validate_prompt(prompt)
        if not is_valid:
            return {"status": "error", "errors": errors}

        # Step 3: Send the prompt to the LLM
        response = await send_to_llm(prompt)

        # Step 4: Validate the response
        is_valid, errors = self.validation_service.validate_response(response)
        if not is_valid:
            return {"status": "error", "errors": errors}

        return {"status": "success", "deployment_plan": response}
