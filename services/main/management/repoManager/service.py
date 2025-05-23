import os
import shutil
from git import Repo, GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from typing import List, Dict
from core.logger import logger
from services.main.utils.caching.redis_service import SessionDataHandler

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
        
        SessionDataHandler.update_session_data(session_id, {"repo_path": repo_path})
        try:
            if os.path.exists(repo_path):
                try:
                    repo = Repo(repo_path)
                    if repo.bare:
                        logger.warning(f"The repository at {repo_path} is bare. Deleting and re-cloning...")
                        shutil.rmtree(repo_path, onerror=self.handle_remove_readonly)
                    else:
                        logger.info(f"Repository already exists at {repo_path}. Returning existing repository.")
                        return repo_path
                except InvalidGitRepositoryError:
                    logger.warning(f"The directory at {repo_path} is not a valid Git repository. Deleting and re-cloning...")
                    shutil.rmtree(repo_path, onerror=self.handle_remove_readonly)

            # Clone the repository if it doesn't exist or was deleted
            logger.info(f"Cloning repository from {repo_url} to {repo_path}...")
            repo = Repo.clone_from(repo_url, repo_path, branch=branch)
            logger.info(f"Repository cloned successfully to {repo_path}.")
            return repo_path

        except (InvalidGitRepositoryError, NoSuchPathError) as e:
            logger.error(f"Error: {e}")
            raise

        except GitCommandError as e:
            logger.error(f"Git command failed: {e}")
            raise

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise

    async def create_files_in_repo(self, repo_path: str, file_objects: List[Dict[str, str]]):
        """
        Create the parsed files in the given repository.

        Args:
            repo (Repo): The GitPython Repo object for the repository.
            file_objects (List[Dict[str, str]]): A list of file objects containing file details.
        """
        for file_object in file_objects:
            file_path = os.path.join(repo_path, file_object["path"])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure the directory exists

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_object["content"])
                logger.info(f"Created file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to create file {file_path}: {e}")
                raise

    def get_folder_and_content(self, files: list) -> tuple:
        """
        Convert a list of files into a folder structure and include their contents.
        Each file should have a path attribute like 'folder1/folder2/file.txt'.
        """
        structure = {}
        contents = {}
        for file in files:
            path_parts = file.get('path').split('/')  # Split the path into folders
            current_dir = structure
            for part in path_parts[:-1]:  # Traverse the path up to the file's folder
                current_dir = current_dir.setdefault(part, {})
            current_dir[path_parts[-1]] = 'file'  # Mark the file in the final folder

            # Read file content (assuming the content is available in the 'file' object)
            contents[file.get('path')] = file.get('content')  # Assuming 'content' attribute contains the file's content

        return structure, contents