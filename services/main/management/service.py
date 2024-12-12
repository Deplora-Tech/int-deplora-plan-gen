from services.main.prompt.service import PromptService
from services.main.validation.service import ValidationService
from services.main.workers.llm_worker import LLMService

class ManagementService:
    def __init__(self):
        self.prompt_service = PromptService()
        self.validation_service = ValidationService()
        self.llm_service = LLMService()

    async def generate_deployment_plan(self, client_id: str, project_id: str, raw_prompt: str, chat_history: dict) :

        if not client_id or not project_id:
            return {"status": "error", "errors": ["Client ID and Project ID are required."]}

        # Step 1: Prepare the structured prompt
        prepared_prompt = self.prompt_service.prepare_prompt(client_id, project_id, raw_prompt, chat_history)

        # Step 3: Generate the deployment plan using LLM
        deployment_plan = await self.llm_service.generate_deployment_plan(prepared_prompt)
        # Step 4: Validate the generated deployment plan
        is_valid, errors = self.validation_service.validate_response(deployment_plan)
        if not is_valid:
            return {"status": "error", "errors": errors}

        # Step 5: Return the final deployment plan
        return {"status": "success", "deployment_plan": deployment_plan}

    def process_feedback(self, client_id: str, project_id: str, feedback: str) -> dict:
        return {"status": "success", "message": f"Feedback for project {project_id} received: {feedback}"}
