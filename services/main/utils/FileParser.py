import re
import os
from typing import List, Dict


class FileParser:
    """
    A parser to identify, extract, and generate file objects from text containing <deploraFile> tags.
    """

    FILE_PATTERN = re.compile(
        r'<deploraFile\s+type="(?P<type>\w+)"\s+filePath="(?P<path>[^"]+)">\n(?P<content>.*?)</deploraFile>',
        re.DOTALL,
    )
    MD_CODE_BLOCK_PATTERN = re.compile(r"^```[\w-]*\n|```$", re.MULTILINE)

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
        matches = self.FILE_PATTERN.finditer(text)
        for match in matches:
            file_type = match.group("type")
            file_path = match.group("path")
            file_content = match.group("content").strip()

            # Remove Markdown code block indicators
            file_content = re.sub(self.MD_CODE_BLOCK_PATTERN, "", file_content)

            file_name = os.path.basename(file_path)
            file_object = {
                "file_name": file_name,
                "type": file_type,
                "path": file_path,
                "content": file_content,
            }

            files.append(file_object)
            files_content.append(match.group(0))
        return files, files_content
