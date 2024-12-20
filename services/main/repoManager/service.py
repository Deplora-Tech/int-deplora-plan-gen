import os
import shutil
from git import Repo, GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from core.logger import logger

class RepoService:
    def __init__(self, root_path: str):
        self.root_path = root_path
    
    def handle_remove_readonly(self, func, path, exc_info):
        """
        Handler for removing read-only files during shutil.rmtree.
        """
        import stat
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            raise

    async def clone_repo(self, repo_url: str, branch: str, session_id: str):
        """
        Clone the repository to the root path using git. If the repository already exists, it pulls the latest changes.
        If the repository is bare, it deletes the directory and clones again.
        
        Args:
            repo_url (str): URL of the repository to clone.
            branch (str): Branch to clone or pull.
            session_id (str): Unique session ID for organizing the repo's path.

        Returns:
            Repo: The GitPython Repo object for the cloned or updated repository.
        """
        repo_path = f"{self.root_path}/{session_id}/{repo_url.split('/')[-1].replace('.git', '')}"
        

        try:
            if os.path.exists(repo_path):
                logger.info(f"The repository at {repo_path} is bare. Deleting and re-cloning...")
                shutil.rmtree(repo_path, onerror=self.handle_remove_readonly)
                logger.info(f"Deleted bare repository at {repo_path}.")

            # Clone the repository if it doesn't exist or was deleted
            logger.info(f"Cloning repository from {repo_url} to {repo_path}...")
            repo = Repo.clone_from(repo_url, repo_path, branch=branch)
            logger.info(f"Repository cloned successfully to {repo_path}.")
            return repo

        except (InvalidGitRepositoryError, NoSuchPathError) as e:
            logger.error(f"Error: {e}")
            raise

        except GitCommandError as e:
            logger.error(f"Git command failed: {e}")
            raise

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise
