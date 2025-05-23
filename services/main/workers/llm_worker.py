from fastapi import HTTPException
from groq import Groq
import anthropic, os
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from core.logger import logger

class LLMService:
    
    
    def __init__(self):
        self.DEFAULT_PLATFORM = "gemini"
        self.DEFAULT_MODELS = {
            "groq": "llama-3.3-70b-specdec",
            "deepseek": "deepseek-coder",
            "claude": "deepseek-3-5-sonnet-20241022",
            "gemini": "gemini-2.0-flash",
            "openai": "gpt-4o",
        }
        
        # Initialize the Groq client
        load_dotenv()
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )
        self.claude = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.deepseek = OpenAI(
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
        self.openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.gemini = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    async def llm_request(self, prompt: str, platform: str = None, model: str = None):
        
        # Set default platform if not provided
        if not platform:
            # if modeel provided
            if model:
                raise HTTPException(
                    status_code=500, detail="Model provided without platform."
                )
            
            platform = self.DEFAULT_PLATFORM
        
        if not model:
            model = self.DEFAULT_MODELS.get(platform)


        if platform == "groq":
            return await self.llm_request_groq(prompt, model)
        elif platform == "deepseek":
            return await self.llm_request_deepseek(prompt, model)
        elif platform == "claude":
            return await self.llm_request_claude(prompt, model)
        elif platform == "gemini":
            return await self.llm_request_gemini(prompt, model)
        elif platform == "openai":
            return await self.llm_request_openai(prompt, model)
        else:
            raise HTTPException(
                status_code=500, detail="Invalid platform specified."
            )


    async def llm_request_groq(self, prompt: str, model: str):
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
                model=model,  # Adjust the model as needed
                temperature=0.5,  # Adjust optional parameters as needed
                max_tokens=8192,
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
        
    async def llm_request_openai(self, prompt: str, model: str):
        try:
            # Generate the chat completion using the OpenAI client
            message = self.openai.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are Deplora, an intelligent deployment assistant designed to generate, analyze, and optimize deployment plans. Your primary goal is to assist users in creating accurate, efficient, and personalized deployment strategies for software applications. Respond with clear and actionable insights, leveraging your expertise in deployment technologies such as Terraform, Docker, Kubernetes, CI/CD pipelines, and cloud platforms. Ensure responses are structured, professional, and align with industry best practices.",
                    },
                    {"role": "user", "content": prompt},
                ],
                stream=False,
            )

            # Extract and return the response content
            content = message.choices[0].message.content
            if not content:
                raise HTTPException(
                    status_code=500, detail="Content not found in the response."
                )

            return content

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        


    async def llm_request_deepseek(self, prompt: str, model: str):
        try:
            logger.info(f"Requesting completion from Deepseek with prompt: {prompt[:50]}...")
            # Generate the chat completion using the Groq client
            message = self.deepseek.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are Deplora, an intelligent deployment assistant designed to generate, analyze, and optimize deployment plans. Your primary goal is to assist users in creating accurate, efficient, and personalized deployment strategies for software applications. Respond with clear and actionable insights, leveraging your expertise in deployment technologies such as Terraform, Docker, Kubernetes, CI/CD pipelines, and cloud platforms. Ensure responses are structured, professional, and align with industry best practices.",
                    },
                    {"role": "user", "content": prompt},
                ],
                stream=False,
            )
            logger.info(f"Received completion from Deepseek.")

            # Extract and return the response content
            content = message.choices[0].message.content
            if not content:
                raise HTTPException(
                    status_code=500, detail="Content not found in the response."
                )

            return content

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def llm_request_claude(self, prompt: str, model: str):
        try:
            # Generate the chat completion using the Groq client
            message = self.claude.messages.create(
                model=model,
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

    
    async def llm_request_gemini(self, prompt: str, model: str):
        try:
            print(model)
            # Generate the chat completion using the Groq client
            message = self.gemini.models.generate_content(
                            model=model, contents=prompt
                        )
            # print(message)
            # Extract and return the response content
            content = message.text
            if not content:
                raise HTTPException(
                    status_code=500, detail="Content not found in the response."
                )
            # print(content)
            return content

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
