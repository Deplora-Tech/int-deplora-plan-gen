

class PromptService:
    
    def get_project_details(self, request: dict):
        """
        Get the project details from the request.
        """
        return request["project_details"]
