class ValidationService:
    def validate_prompt(self, prompt: str):
        if not prompt:
            return False, ["Prompt cannot be empty."]
        return True, []

    def validate_response(self, response):
        if "error" in response:
            return False, ["Invalid response from LLM."]
        return True, []
