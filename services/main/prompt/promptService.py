from services.knowledgebase import api as knowledgebase_api
import asyncio


class PromptService:
    
    async def get_project_details(self, request: dict):
        """
        Get the project details from the request.
        """
        return request["project_details"]
    
    async def get_user_preferences(self, request: dict):
        """
        Get the user preferences from the request.
        """
        username = "User 3"
        prompt = "Deploy an application to AWS using ECS. Ensure it has a load balancer in front, deploy across multiple AZs for resilience, and use CloudWatch for monitoring"
        user_preferences = await knowledgebase_api.update_context(username, prompt)
        print(user_preferences)
        return user_preferences


