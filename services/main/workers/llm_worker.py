import asyncio
import aiohttp

class LLMService:
    async def generate_deployment_plan(self, prompt: str) -> str:

        API_URL = "https://api-inference.huggingface.co/models/Salesforce/xLAM-1b-fc-r"
        HEADERS = {"Authorization": "Bearer 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"}

        payload = {"inputs": prompt}

        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=HEADERS, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result[0].get("generated_text", "No generated text found.")
                else:
                    return f"Error: {response.status} - {await response.text()}"


