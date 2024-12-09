class PromptService:
    def prepare_prompt(self, request: dict) -> str:
        application = request.get("application", {})
        environment = request.get("environment", {})
        infrastructure = request.get("infrastructure", {})

        prompt = f"""
        Generate a deployment plan for the following application:
        - Application Name: {application.get('name', 'Unknown')}
        - Type: {application.get('type', 'Unknown')}
        - Environment: {environment.get('type', 'Unknown')}
        - Cloud Provider: {infrastructure.get('provider', 'Unknown')}
        """
        return prompt
