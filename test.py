from services.knowledgebase import api as knowledgebase_api

import asyncio



async def main():
    await knowledgebase_api.setup_context_graph("bolt://localhost:7687")
    await knowledgebase_api.add_user("test_user", "Test Organization")


asyncio.run(main())