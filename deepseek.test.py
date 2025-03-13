import asyncio
from services.main.workers import llm_worker

async def main():
    llm = llm_worker.LLMService()
    response = await llm.llm_request("Deploy this to aws", platform="deepseek")
    print(response)

if __name__ == "__main__":
    # Run the async function using asyncio
    asyncio.run(main())


# Please install OpenAI SDK first: `pip3 install openai`

# from openai import OpenAI
# from dotenv import load_dotenv
# import os

# load_dotenv()
# client = OpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

# response = client.chat.completions.create(
#     model="deepseek-coder",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant"},
#         {"role": "user", "content": "Deploy this to aws"},
#     ],
#     stream=False
# )

# print(response.choices[0].message.content)