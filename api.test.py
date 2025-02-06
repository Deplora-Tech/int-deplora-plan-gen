# import asyncio
# from services.main.management.api import handle_message
# from services.main.communication.models import MessageRequest
# from services.main.communication.service import CommunicationService
# from services.main.workers import llm_worker


# async def main():
#     # Call the async function here with await
#     # await handle_message(
#     #     MessageRequest(
#     #         message="Deploy this to aws",
#     #         client_id="123",
#     #         project_id="123",
#     #         organization_id="123",
#     #         session_id="123",
#     #         chat_history={},
#     #     )
#     #     , CommunicationService()
#     # )
#     llm = llm_worker.LLMService()
#     response = await llm.llm_request("Deploy this to aws", platform="gemini")
#     print(response)

# if __name__ == "__main__":
#     # Run the async function using asyncio
#     asyncio.run(main())


import re

CDATA_PATTERN = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)

text = """<![CDATA[
# Example variable overrides
# aws_region = "us-west-2"
# subnet_ids = ["subnet-xxxxxxxxxxxxxxxxx", "subnet-yyyyyyyyyyyyyyyyy"]
# security_groups = ["sg-xxxxxxxxxxxxxxxxx"]
]]>"""

match = CDATA_PATTERN.search(text)
if match:
    print("Matched Content:\n", match.group(1))  # Extracts content inside CDATA
else:
    print("No match found.")
