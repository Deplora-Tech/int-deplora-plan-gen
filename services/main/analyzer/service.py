import os
import json
from services.main.utils.prompts.service import PromptManagerService
from services.main.workers.llm_worker import LLMService
from gitingest import ingest


class AnalyzerService:
    def __init__(self):
        self.llm_service = LLMService()
        self.prompt_manager = PromptManagerService()

    async def identify_deployment_files(
        self, repo_path: str, template_path: str
    ) -> list:
        """
        Identifies files in the repository that may contain deployment-related information.

        :param repo_path: Path to the Git repository.
        :param template_path: Path to the described_template_dict.json file.
        :return: List of files that may contain deployment-related information.
        """
        # Load the JSON template from the provided path
        with open(template_path, "r", encoding="utf-8") as file:
            template_content = file.read()

        # Use GitIngest to analyze the repository structure
        summary, tree, content = ingest(repo_path)

        # Prepare the prompt for the LLM
        prompt = f"""
        You are an intelligent assistant tasked with analyzing a Git repository structure to identify files
        that may contain deployment-related information. Below is the JSON structure describing deployment information:

        {template_content}

        Here is the Git repository structure:

        {tree}

        Your task:
        - Identify and return a **JSON array** of file paths that may contain deployment-related information.
        - Only include file paths that are likely to help fill fields in the provided JSON structure.
        - STRICTLY OUTPUT ONLY A VALID JSON ARRAY. Do not include explanations, comments, or any additional text.
        """

        # Send the prompt to the LLM and get the response
        response = await self.llm_service.llm_request(prompt)

        try:
            # Parse the response as JSON
            identified_files = json.loads(response.strip())
            if not isinstance(identified_files, list):
                raise ValueError("The LLM response is not a valid list.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            raise ValueError(f"Failed to process LLM response: {e}")

        return identified_files

    async def fill_json_template(
        self,
        file_name: str,
        file_content: str,
        described_template: dict,
        current_template: dict,
    ) -> dict:
        """
        Fills the current JSON template using the provided file content and described template.

        :param file_name: The name of the file
        :param file_content: The content of the file to analyze.
        :param described_template: The detailed template describing all fields and their descriptions.
        :param current_template: The current (possibly empty) JSON template to fill.
        :return: The modified JSON template with extracted details.
        """
        # Convert the templates to JSON strings for the prompt
        described_template_json = json.dumps(described_template, indent=4)
        current_template_json = json.dumps(current_template, indent=4)

        # Prepare the prompt for the LLM
        # Updated prompt in the fill_json_template function
        prompt = f"""
        You are an intelligent assistant tasked with analyzing the content of a specific file and filling in the provided JSON template.
        Use the detailed field descriptions from the described template to understand the purpose and format of each field.

        **Important Context**:
        - The file being analyzed is: `{file_name}`.
        - Consider whether it is appropriate to fill certain fields based on the file's purpose and typical content:
          - Configuration files typically define runtime environments, environment variables, and networking configurations.
          - Build files describe the build process and runtime dependencies.
          - Dependency files list application dependencies, versions, and metadata like application name and description.
          - Source code files reveal application frameworks, ports, and logging configurations but rarely contain deployment-specific details.
          - CI/CD pipeline files define automated workflows for building, testing, and deploying the application.
          - Documentation files provide metadata or instructions and may describe the application or its deployment process.

        **Additional Requirement**:
        - For single-valued fields (e.g., "name", "description"), append the file name in this format: `|{file_name}|` after the value.
          - Example: `"name": "awesome-app |readme.md|`.

        **Described Template (Field Descriptions)**:
        {described_template_json}

        **File Content**:
        {file_content}

        **Current Template (To Be Filled)**:
        {current_template_json}

        **Your Task**:
        - Analyze the file content and fill as many fields in the JSON template as possible.
        - Ensure all filled fields adhere to the descriptions provided in the Described Template.
        - Append the file name as `|{file_name}|` for single-valued fields.
        - Carefully evaluate whether it is appropriate to populate a field based on the file content and its typical purpose.
        - If a field cannot be filled or is irrelevant based on the file type, leave it unchanged in the Current Template.
        - STRICTLY return the modified JSON template as output without any additional explanations or comments.
        """

        # Send the prompt to the LLM and get the response
        response = await self.llm_service.llm_request(prompt)

        # Clean the LLM response by removing code block markers and trimming whitespace
        cleaned_response = response.strip().strip("```json").strip("```")

        if not cleaned_response:
            raise ValueError("LLM response is empty after cleaning.")

        try:
            # Parse the modified JSON template
            modified_template = json.loads(cleaned_response)
            if not isinstance(modified_template, dict):
                raise ValueError("The LLM response is not a valid dictionary.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")

        return modified_template

    async def compare_single_valued_field(
        self, field_name: str, value1, value2, field_description: str
    ) -> str:
        """
        Compares two values for a single-valued field using the field description to decide the most relevant value.

        :param field_name: The name of the field being compared.
        :param value1: The first value to compare.
        :param value2: The second value to compare.
        :param field_description: The description of the field to guide the comparison.
        :return: The most relevant value for the field.
        """
        # Ensure values are strings
        value1 = str(value1) if value1 is not None else ""
        value2 = str(value2) if value2 is not None else ""

        # Extract file names from the values if present
        value1_file = value1.split("|")[-1] if "|" in value1 else "unknown"
        value2_file = value2.split("|")[-1] if "|" in value2 else "unknown"

        prompt = f"""
        You are an intelligent assistant tasked with comparing two values for a specific field in a JSON structure.

        Field Name: {field_name}
        Field Description: {field_description}

        - Value 1: {value1} (from file `{value1_file}`)
        - Value 2: {value2} (from file `{value2_file}`)

        Your task:
        - Compare the two values based on the field description.
        - Decide which value is more relevant and explain your reasoning.
        - STRICTLY return the most relevant value as plain text without any additional comments or formatting.
        """
        response = await self.llm_service.llm_request(prompt)
        return response.strip()

    def parse_repo_contents(self, repo_contents: str) -> dict:
        """
        Parses the repository content into a dictionary of file paths and their contents.

        :param repo_contents: The raw string content of the repository.
        :return: A dictionary with normalized file paths as keys and file contents as values.
        """
        files = {}
        sections = repo_contents.split(
            "================================================"
        )

        for i in range(1, len(sections), 2):
            file_header = sections[i].strip()
            if file_header.startswith("File:"):
                # Normalize the file path (remove leading slashes and backslashes)
                file_path = (
                    file_header.split("File:")[-1]
                    .strip()
                    .lstrip("/")
                    .replace("\\", "/")
                )
                file_content = sections[i + 1].strip()
                files[file_path] = file_content

        return files

    def find_matching_file(self, file_name: str, parsed_contents: dict) -> str:
        """
        Finds a matching file in the parsed contents using exact or approximate matching.

        :param file_name: The file name to search for.
        :param parsed_contents: Dictionary of parsed repository contents.
        :return: The matched file content or None if no match is found.
        """
        # Normalize the file name
        normalized_file_name = file_name.lstrip("/").replace("\\", "/")

        # Exact match
        if normalized_file_name in parsed_contents:
            return parsed_contents[normalized_file_name]

        # Fallback: Approximate match by file name
        for key in parsed_contents.keys():
            if key.endswith(normalized_file_name):
                return parsed_contents[key]

        return None

    async def merge_templates(
        self, base_template: dict, updated_template: dict, described_template: dict
    ) -> dict:
        """
        Merges an updated template into a base template, preserving existing details and appending to multi-valued fields.

        :param base_template: The original template with existing data.
        :param updated_template: The new template with updates from the latest file.
        :param described_template: The detailed template describing all fields and their descriptions.
        :return: The merged template.
        """
        for key, value in updated_template.items():
            if isinstance(value, dict):
                # Recursively merge dictionaries
                base_template[key] = await self.merge_templates(
                    base_template.get(key, {}), value, described_template.get(key, {})
                )
            elif isinstance(value, list):
                # Merge lists of dictionaries or primitive values
                if isinstance(base_template.get(key), list):
                    if all(isinstance(item, dict) for item in value):
                        # Handle lists of dictionaries (e.g., dependencies)
                        existing_items = base_template.get(key, [])
                        for new_item in value:
                            if new_item not in existing_items:
                                existing_items.append(new_item)
                        base_template[key] = existing_items
                    else:
                        # Handle lists of primitive values
                        base_template[key] = list(
                            set(base_template.get(key, []) + value)
                        )
                else:
                    # If base is not a list, replace it with the new value
                    base_template[key] = value
            elif isinstance(base_template.get(key), list):
                # If base is a list but value is not, replace the list with the new value
                base_template[key] = value
            else:
                # Handle single-valued fields
                existing_value = base_template.get(key)
                if existing_value:
                    # Compare existing value with the new value using LLM
                    field_description = described_template.get(
                        key, "No description available."
                    )
                    best_value = await self.compare_single_valued_field(
                        field_name=key,
                        value1=existing_value,
                        value2=value,
                        field_description=field_description,
                    )
                    base_template[key] = best_value
                else:
                    # If no existing value, use the new value
                    base_template[key] = value
        return base_template

    async def optimize_template(
        self, current_template: dict, described_template: dict
    ) -> dict:
        """
        Optimizes the JSON template by:
        1. Removing file name references (e.g., "|readme.md|") from single-valued fields.
        2. Refining the template to better match the described template using the LLM.

        :param current_template: The filled JSON template.
        :param described_template: The detailed template describing all fields and their descriptions.
        :return: The optimized JSON template.
        """

        # Step 1: Remove file name references from single-valued fields
        def clean_single_valued_fields(template, described):
            for key, value in template.items():
                if isinstance(value, dict):
                    # Recursively clean nested dictionaries
                    template[key] = clean_single_valued_fields(
                        value, described.get(key, {})
                    )
                elif isinstance(value, str):
                    # Remove file name references for single-valued fields
                    template[key] = value.split("|")[0].strip()
                elif isinstance(value, list):
                    # Handle lists by recursively cleaning nested dictionaries in lists
                    if all(isinstance(item, dict) for item in value):
                        template[key] = [
                            clean_single_valued_fields(item, described.get(key, {}))
                            for item in value
                        ]
            return template

        cleaned_template = clean_single_valued_fields(
            current_template, described_template
        )

        # Step 2: Use LLM to refine the template further
        described_template_json = json.dumps(described_template, indent=4)
        cleaned_template_json = json.dumps(cleaned_template, indent=4)

        prompt = f"""
        You are an intelligent assistant tasked with optimizing a JSON template to ensure it is accurate, concise, and aligned with the described template.

        **Optimization Rules**:
        1. Retain all valid, non-redundant information.
        2. Remove:
           - Duplicates or redundant entries in multi-valued fields.
           - Useless or irrelevant information that does not align with the described template.
        3. Leave fields that are empty or not applicable unchanged.
        4. Ensure the JSON structure strictly adheres to the described template, including field names and types.
        5. Do not add new information or fill empty fields; focus solely on refining the existing content.
        6. Preserve the integrity of the information while ensuring consistency and alignment with the described template.

        **Described Template (Field Descriptions)**:
        {described_template_json}

        **JSON to Optimize**:
        {cleaned_template_json}

        **Your Task**:
        - Analyze the provided JSON template and optimize it according to the rules above.
        - Return the optimized JSON template as the output.
        - STRICTLY return only the JSON structure as output, without any additional explanations or comments.
        """

        response = await self.llm_service.llm_request(prompt)

        # Clean the LLM response and parse it as JSON
        cleaned_response = response.strip().strip("```json").strip("```")
        if not cleaned_response:
            raise ValueError("LLM response is empty after cleaning.")

        try:
            optimized_template = json.loads(cleaned_response)
            if not isinstance(optimized_template, dict):
                raise ValueError("The LLM response is not a valid dictionary.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")

        return optimized_template

    async def process_files_and_update_template(
        self, repo_path: str, described_template_path: str, empty_template_path: str
    ) -> dict:
        """
        Processes files identified from the repository and updates the JSON template file by file.
        Resolves conflicts for single-valued fields using the LLM.

        :param repo_path: Path to the Git repository.
        :param described_template_path: Path to the described template JSON file.
        :param empty_template_path: Path to the initial empty JSON template.
        :return: The final filled JSON template.
        """
        # Load the described template and empty template
        with open(described_template_path, "r", encoding="utf-8") as f:
            described_template = json.load(f)

        with open(empty_template_path, "r", encoding="utf-8") as f:
            current_template = json.load(f)

        # Identify deployment-related files
        files = await self.identify_deployment_files(repo_path, described_template_path)

        if not files:
            print("No deployment-related files found.")
            return current_template

        print(f"Files identified: {files}")

        # Use GitIngest to get the repository content
        _, _, repo_contents = ingest(repo_path)

        # Parse the repository contents into a dictionary
        parsed_contents = self.parse_repo_contents(repo_contents)

        for file_name in files:
            print(f"Processing file: {file_name}")

            # Retrieve file content with exact or approximate matching
            file_content = self.find_matching_file(file_name, parsed_contents)
            if not file_content:
                print(f"File {file_name} not found in repository contents. Skipping.")
                continue

            # Fill the JSON template using the current file
            updated_template = await self.fill_json_template(
                file_name=file_name,
                file_content=file_content,
                described_template=described_template,
                current_template=current_template,
            )

            # print(f"Updated template after processing {file_name}: {json.dumps(updated_template, indent=4)}")
            # Merge the updated template into the current template
            current_template = await self.merge_templates(
                current_template, updated_template, described_template
            )
            # print(f"Updated template after processing {file_name}: {json.dumps(current_template, indent=4)}")

        current_template = await self.optimize_template(
            current_template, described_template
        )

        return current_template
