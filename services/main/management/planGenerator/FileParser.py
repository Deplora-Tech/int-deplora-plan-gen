import os
import json
from typing import List, Dict
from core.logger import logger


class FileParser:
    """
    A parser to identify, extract, and generate file objects from text containing <deploraFile> tags.
    """

    def __init__(self):
        """
        Initialize the parser with a base directory where files can be saved.
        """
        pass

    def parse(self, text: str) -> List[Dict[str, str]]:
        """
        Parse the input text and extract file details.

        Args:
            text (str): The input text containing <deploraFile> tags.

        Returns:
            List[Dict[str, str]]: A list of file objects containing file details.
        """
        files = []
        files_content = []

        # Start and end markers for the <deploraFile> tag
        file_start_tag = "<deploraFile"
        file_end_tag = "</deploraFile>"

        # Iterate over the text to find file blocks
        start_pos = 0
        while True:
            start_pos = text.find(file_start_tag, start_pos)
            if start_pos == -1:
                break

            # Find the corresponding end tag
            end_pos = text.find(file_end_tag, start_pos)
            if end_pos == -1:
                break

            # Extract the file block and process it
            file_block = text[start_pos:end_pos + len(file_end_tag)]

            # Extract file type, filePath and action from the <deploraFile> tag
            file_type_start = file_block.find('type="') + len('type="')
            file_type_end = file_block.find('"', file_type_start)
            file_type = file_block[file_type_start:file_type_end]

            file_path_start = file_block.find('filePath="') + len('filePath="')
            file_path_end = file_block.find('"', file_path_start)
            file_path = file_block[file_path_start:file_path_end]

            file_action_start = file_block.find('action="') + len('action="')
            if file_action_start != -1:
                file_action_end = file_block.find('"', file_action_start)
                file_action = file_block[file_action_start:file_action_end]
            else:
                file_action = "create"

            # Extract content from between the tags
            content_start = file_block.find('>', file_block.find(file_start_tag)) + 1
            content_end = file_block.rfind('<', file_block.find(file_end_tag))
            file_content = file_block[content_start:content_end].strip()

            # Clean up content (removing Markdown code blocks and CDATA)
            # Remove Markdown code blocks (```)
            file_content = self.remove_markdown_code_blocks(file_content)

            # Remove CDATA tags
            if "<![CDATA[" in file_content and "]]>" in file_content:
                cdata_start = file_content.find("<![CDATA[") + len("<![CDATA[")
                cdata_end = file_content.find("]]>", cdata_start)
                file_content = file_content[cdata_start:cdata_end]

            # Prepare the file object and append it to the result
            file_name = os.path.basename(file_path)
            file_object = {
                "file_name": file_name,
                "type": file_type,
                "path": file_path,
                "content": file_content,
                "action": file_action,
            }

            files.append(file_object)
            files_content.append(file_block)

            # Move the position to the next possible file tag
            start_pos = end_pos + len(file_end_tag)

        if len(files) == 0:
            raise ValueError("No files found in the input text.")

        return files, files_content
    
    @staticmethod
    def parse_json( text: str) -> Dict:
        """
        Parse the input text and extract json details.

        Args:
            text (str): The input text containing json.

        Returns:
            Dict: A json object containing json details.
        """
        # Clean up the text before parsing
        text = "{".join(text.split("{")[1:])
        text = "}".join(text.split("}")[:-1])
        return json.loads(f"{{{text}}}")
    
    def remove_markdown_code_blocks(self, content: str) -> str:
        """
        Removes Markdown code blocks from the content.

        Args:
            content (str): The content to remove code blocks from.

        Returns:
            str: The content with code blocks removed.
        """
        # Remove Markdown code blocks wrapped in triple backticks
        in_code_block = False
        result = []
        for line in content.split("\n"):
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue  # Skip the line with the opening or closing ```
            if not in_code_block:
                result.append(line)
        return "\n".join(result).strip()
