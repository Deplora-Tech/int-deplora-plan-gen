class ValidationService:
    def validate_prompt(self, prompt: str):
        if not prompt:
            return False, ["Prompt cannot be empty."]
        return True, []

    def validate_response(self, response: str):
        if "error" in response.lower():
            return False, ["Invalid response from LLM."]
        return True, []
