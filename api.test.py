import asyncio
from services.main.management.api import handle_message
from services.main.communication.models import MessageRequest
from services.main.communication.service import CommunicationService


async def main():
    # Call the async function here with await
    await handle_message(
        MessageRequest(
            message="Deploy this to aws",
            client_id="123",
            project_id="123",
            organization_id="123",
            session_id="123",
            chat_history={},
        )
        , CommunicationService()
    )


if __name__ == "__main__":
    # Run the async function using asyncio
    asyncio.run(main())
