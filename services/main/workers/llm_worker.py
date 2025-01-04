from fastapi import HTTPException
from groq import Groq
import anthropic, os
from dotenv import load_dotenv


class LLMService:
    def __init__(self):
        # Initialize the Groq client
        load_dotenv()
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)
        self.claude = anthropic.Anthropic( api_key=os.environ.get("ANTHROPIC_API_KEY"))
        

    async def llm_request(self, prompt: str):
        try:
            # Generate the chat completion using the Groq client
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are Deplora, an intelligent deployment assistant designed to generate, analyze, and optimize deployment plans. Your primary goal is to assist users in creating accurate, efficient, and personalized deployment strategies for software applications. Respond with clear and actionable insights, leveraging your expertise in deployment technologies such as Terraform, Docker, Kubernetes, CI/CD pipelines, and cloud platforms. Ensure responses are structured, professional, and align with industry best practices.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model="llama-3.3-70b-versatile",  # Adjust the model as needed
                temperature=0.5,  # Adjust optional parameters as needed
                max_tokens=32768,
                top_p=1,
                stop=None,
                stream=False,
            )

            # Extract and return the response content
            content = chat_completion.choices[0].message.content
            if not content:
                raise HTTPException(
                    status_code=500, detail="Content not found in the response."
                )

            return content
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def llm_request_claude(self, prompt: str):
        try:
            # Generate the chat completion using the Groq client
            message = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "system",
                        "content": "You are Deplora, an intelligent deployment assistant designed to generate, analyze, and optimize deployment plans. Your primary goal is to assist users in creating accurate, efficient, and personalized deployment strategies for software applications. Respond with clear and actionable insights, leveraging your expertise in deployment technologies such as Terraform, Docker, Kubernetes, CI/CD pipelines, and cloud platforms. Ensure responses are structured, professional, and align with industry best practices.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            
            # Extract and return the response content
            content = message.content
            if not content:
                raise HTTPException(
                    status_code=500, detail="Content not found in the response."
                )
                
            return content
        
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
