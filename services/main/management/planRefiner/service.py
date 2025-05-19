from services.main.utils.caching.redis_service import SessionDataHandler
from services.main.management.planGenerator.FileParser import FileParser
from services.main.workers.llm_worker import LLMService
from core.logger import logger


class PlanRefinerService:
    def __init__(self):
        self.file_parser = FileParser()
        self.llm_service = LLMService()

    async def run_change_agent(self, prompt: str, current_files:dict) -> dict:
    

        # Generate the changed files based on the prompt and current files
        changed_files = await self.generate_file_changes(prompt, current_files)
        changed_files_map_by_action = {}

        for file in changed_files:
            file_action = file.get("action")
            if file_action not in changed_files_map_by_action:
                changed_files_map_by_action[file_action] = []
            changed_files_map_by_action[file_action].append(file)


        # Merge the current files with the changed files based on the action
        merged_files = self.merge_files(current_files, changed_files_map_by_action)
        print(f"Merged files: {[file["path"] for file in changed_files]}")
        
        return merged_files, changed_files

    def merge_files(self, current_files: dict, changed_files: dict) -> dict:
        """
        Merge the current files with the changed files based on the action.
        """
        for action, files in changed_files.items():
            if action == "modify":
                for file in files:
                    file_path = file.get("path")
                    current_files[file_path] = file.get("content")
            elif action == "create":
                for file in files:
                    file_path = file.get("path")
                    current_files[file_path] = file.get("content")
            elif action == "delete":
                for file in files:
                    file_path = file.get("path")
                    if file_path in current_files:
                        del current_files[file_path]
        return current_files

    async def generate_file_changes(self, prompt: str, current_files: dict) -> dict:
        """
        Run the change agent with the provided prompt and current files.
        """
        PROMPT = f"""
        You are a change agent for a deployment plan. Your task is to modify the deployment plan based on the user's request.
        User request: {prompt}
        Files: {current_files}

        Your task is
        1. Identify the files that need to be changed.
        2. Rewrite the files with the changes, include them in the response with action="modify".
        3. If new files are created, include them in the response with action="create". The files should be modular.
        4. If files are deleted, indicate that in the response with action="delete".
            <deploraFile type="fileType" filePath="filePath" action="delete"> </deploraFile>
        5. Only change the code blocks that are necessary to fulfill the user's request within a file.
        6. Return the files in the same format as below:

        <deploraFile type="fileType" filePath="filePath" action="modify | create | delete">
        file content
        </deploraFile>
        
        Ensure that the file content is valid and follows the correct format.
        """

        # Call the LLM service to get the response
        try:
            response = await self.llm_service.llm_request(PROMPT, platform="deepseek")
            # print(f"Change agent response: {response}")
            files, files_content = self.file_parser.parse(response)
            # print(f"Parsed files: {files}")
            return files
        except Exception as e:
            logger.error(f"Error running change agent: {e}")
            return []


### Example usage
if __name__ == "__main__":

    rf = PlanRefinerService()
    import asyncio

    asyncio.run(rf.run_change_agent("Add a load balancer. Delete the readme file", "9557b789-71d1-419b-9c58-3f55232d2d73"))

    # run_change_agent("Change the instance_class of mydb to db.t3.large", fake_files)
