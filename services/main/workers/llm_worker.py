from fastapi import HTTPException
import requests


class LLMService:
    async def generate_deployment_plan(self, prompt: str):
        api_url = "https://api.groq.com/openai/v1/chat/completions"
        api_key = "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"  # Store your API key as an environment variable
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        # Payload for the POST request
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }

        try:
            # Make the POST request
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx

            # Extract JSON response
            response_json = response.json()

            # Extract the 'content' field from the response
            content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                raise HTTPException(status_code=500, detail="Content not found in the response.")

            return content
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))
