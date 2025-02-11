import asyncio
from services.main.management.api import handle_message
from services.main.communication.models import MessageRequest
from services.main.communication.service import CommunicationService
from services.main.workers import llm_worker
from services.main.excecutor.JenkinsManager import JenkinsManager
import time

async def main():
    # Call the async function here with await
    # await handle_message(
    #     MessageRequest(
    #         message="Deploy this to aws",
    #         client_id="123",
    #         project_id="123",
    #         organization_id="123",
    #         session_id="123",
    #         chat_history={},
    #     )
    #     , CommunicationService()
    # )
    llm = llm_worker.LLMService()
    response = await llm.llm_request("Deploy this to aws", platform="deepseek")
    print(response)

if __name__ == "__main__":
    # Run the async function using asyncio
    asyncio.run(main())

# jenkins = JenkinsManager()

# jenkins.create_folder("1")
# jenkins.create_local_pipeline(
#     "1", "d114e906-957a-428f-b1af-6c47bb6577c4", "/home/sahiru/deplora/repo-clones/d114e906-957a-428f-b1af-6c47bb6577c4/po-server"
# )

# build_id = jenkins.trigger_pipeline_build("1", "d114e906-957a-428f-b1af-6c47bb6577c4")

# x = 0
# build_info = {"building": True}
# while build_info["building"]:
#     stages_info = jenkins.get_stages_info(
#         "1", "d114e906-957a-428f-b1af-6c47bb6577c4", build_id
#     )

#     build_info["stages"] = stages_info
#     print(build_info)
#     time.sleep(2)
#     x += 1
#     # if x >= 100:
#     #     break