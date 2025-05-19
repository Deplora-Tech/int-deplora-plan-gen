from core.database import analysis_results
from services.main.analyzer.service import AnalyzerService
from core.config import settings
import logging
import nest_asyncio



nest_asyncio.apply()
logger = logging.getLogger(__name__)


async def run_analyzer_task(client_id: str, project_id: str, repo_url: str):
    analyzer_service = AnalyzerService()
    described_template_path = settings.DESCRIBED_TEMPLATE_PATH
    empty_template_path = settings.INIT_TEMPLATE_PATH

    try:
        logger.info(
            f"Starting analysis for repo_url: {repo_url}, project_id: {project_id}"
        )
        # Process the repository
        generated_template = await analyzer_service.process_files_and_update_template(
            repo_path=repo_url,
            described_template_path=described_template_path,
            empty_template_path=empty_template_path,
        )

        # Store the result in MongoDB
        db_entry = {
            "client_id": client_id,
            "project_id": project_id,
            "repo_url": repo_url,
            "generated_template": generated_template,
        }
        await analysis_results.insert_one(db_entry)
        logger.info(
            f"Analysis completed and stored for client_id={client_id}, project_id={project_id}"
        )

    except Exception as e:
        # Log the error instead of raising HTTPException
        logger.error(
            f"Error during analysis for project_id={project_id}, client_id={client_id}: {e}"
        )


async def get_generated_template(project_id: str) -> dict:
    """
    Retrieve the generated template for a specific project ID.

    :param project_id: The project ID to search for in the database.
    :return: The document containing the generated template.
    :raises ValueError: If no document is found for the given project ID.
    """
    try:
        # Query the database for the specific project_id
        result = await analysis_results.find_one({"project_id": project_id})

        if not result:
            raise ValueError(f"No generated template found for project_id={project_id}")

        # Serialize the ObjectId to a string for compatibility
        result["_id"] = str(result["_id"])
        return result

    except Exception as e:
        # Log the error and re-raise for handling
        logging.error(
            f"Error fetching generated template for project_id={project_id}: {e}"
        )
        raise
