import asyncio
import logging

# Import your function and dependencies
from services.main.analyzer.api import get_generated_template

logging.basicConfig(level=logging.DEBUG)

class ProjectService:
    async def retrieve_project_details(self, project_id: str) -> dict:
        logging.debug("Retrieving project details...")
        full_doc = await get_generated_template(project_id)
        project_data = full_doc.get("generated_template", {})
        await asyncio.sleep(3)
        return project_data


async def main():
    service = ProjectService()
    project_id = "67890"  # replace with a real project ID
    details = await service.retrieve_project_details(project_id)
    print(details)

if __name__ == "__main__":
    asyncio.run(main())
