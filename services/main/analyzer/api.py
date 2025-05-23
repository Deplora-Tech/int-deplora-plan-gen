from core.database import analysis_results, user_projects
from services.main.analyzer.service import AnalyzerService
from core.config import settings
import logging
import nest_asyncio
import os, asyncio


nest_asyncio.apply()
logger = logging.getLogger(__name__)


async def run_analyzer_task(client_id: str, project_id: str, repo_url: str, branch: str):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(base_dir, "../../../"))  # Navigate to project root
        empty_template_path = os.path.join(root_dir, settings.INIT_TEMPLATE_PATH)
        described_template_path = os.path.join(root_dir, settings.DESCRIBED_TEMPLATE_PATH)



        analyzer_service = AnalyzerService()

        # Pre-create document with pending status
        db_entry = {
            "client_id": client_id,
            "_id": project_id,
            "repo_url": repo_url,
            "status": "pending",
            "branch": branch,
            "generated_template": None,
        }   

    
        # Insert initial entry
        result = await analysis_results.insert_one(db_entry)
        doc_id = result.inserted_id

        logger.info(
            f"Starting analysis for repo_url: {repo_url}, project_id: {project_id}"
        )

        # Run the analyzer
        generated_template = await analyzer_service.process_files_and_update_template(
            repo_path=repo_url,
            branch=branch,
            described_template_path=described_template_path,
            empty_template_path=empty_template_path,
        )

        # Update document with results
        await analysis_results.update_one(
            {"_id": doc_id},
            {
                "$set": {
                    "generated_template": generated_template,
                    "status": "success",
                }
            }
        )

        # Update user_projects collection projects which is a list of project ids
        # Check if a document with the given project_id exists
        # existing_project = await user_projects.find_one({"projects": project_id})
        # if existing_project:
        #     # Update the document to ensure the project_id is in the list (idempotent)
        #     await user_projects.update_one(
        #     {"_id": existing_project["_id"]},
        #     {"$addToSet": {"projects": project_id}}
        #     )
        # else:
        #     # Upsert: create a new document if client_id doesn't exist, or add project_id to existing
        #     await user_projects.update_one(
        #     {"client_id": client_id},
        #     {"$addToSet": {"projects": project_id}},
        #     upsert=True
        #     )

        logger.info(
            f"Analysis completed and stored for client_id={client_id}, project_id={project_id}"
        )
    

    except Exception as e:
        # Update document with error status
        await analysis_results.update_one(
            {"_id": project_id},
            {
                "$set": {
                    "status": "error",
                    "error_message": str(e),
                }
            }
        )
        logger.error(
            f"Error during analysis for project_id={project_id}, client_id={client_id}: {e}",
            exc_info=True
        )



async def get_generated_template(project_id: str) -> dict:
    """
    Retrieve the generated template for a specific project ID.

    :param project_id: The project ID to search for in the database.
    :return: The document containing the generated template.
    :raises ValueError: If no document is found for the given project ID.
    """
    try:
        logger.info(f"Fetching generated template for project_id={project_id}")
        # Query the database for the specific project_id
        result = await analysis_results.find_one({"_id": project_id})

        if not result:
            raise ValueError(f"No generated template found for project_id={project_id}")
        
        if result.get("status") == "error":
            raise ValueError(
                f"Error occurred during analysis for project_id={project_id}: {result.get('error_message')}"
            )
        
        doc = result.get("generated_template", {})

        while not doc and result.get("status") == "pending":
            # Wait for a short period before checking again
            await asyncio.sleep(2)
            result = await analysis_results.find_one({"_id": project_id})
            doc = result.get("generated_template", {})
            logger.info(
                f"Waiting for analysis to complete for project_id={project_id}..."
            )

        logger.info(
            f"Generated template retrieved for project_id={project_id}: {doc}"
        )
        return doc

    except Exception as e:
        # Log the error and re-raise for handling
        logging.error(
            f"Error fetching generated template for project_id={project_id}: {e}"
        )
        raise


async def get_projects_by_user_id(client_id: str) -> list:
    # Step 1: Get project_ids for the user
    # user_doc = await user_projects.find_one({"client_id": client_id})
    
    # if not user_doc or "projects" not in user_doc:
    #     return []

    # project_ids = user_doc["projects"]
    # print(f"Project IDs for client_id {client_id}: {project_ids}")

    # Step 2: Fetch details from analysis_results
    cursor = analysis_results.find({"client_id": client_id, "status": "success"})
    projects = await cursor.to_list(length=None)
    
    for project in projects:
        project["project_id"] = str(project["_id"])
        del project["generated_template"]

    return projects