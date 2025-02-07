import re
import os, json
from typing import List, Dict
from core.logger import logger


class FileParser:
    """
    A parser to identify, extract, and generate file objects from text containing <deploraFile> tags.
    """

    FILE_PATTERN = re.compile(
        r'<deploraFile\s+type="(?P<type>\w+)"\s+filePath="(?P<path>[^"]+)">\n(?P<content>.*?)</deploraFile>',
        re.DOTALL,
    )
    MD_CODE_BLOCK_PATTERN = re.compile(r"^```[\w-]*\n|```$", re.MULTILINE)
    CDATA_PATTERN = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)


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
            try:
                file_type = match.group("type")
                file_path = match.group("path")
                file_content = match.group("content").strip()

                # Remove Markdown code block indicators
                file_content = re.sub(self.MD_CODE_BLOCK_PATTERN, "", file_content)
                
                # Remove CDATA tags
                file_content = re.sub(self.CDATA_PATTERN, r"\1", file_content)

                file_name = os.path.basename(file_path)
                file_object = {
                    "file_name": file_name,
                    "type": file_type,
                    "path": file_path,
                    "content": file_content,
                }

                files.append(file_object)
                files_content.append(match.group(0))
            except Exception as e:
                logger.error(f"Error parsing file: {e}")
                logger.error(f"Match: {match.group(0)}")
                continue
        
        if not files:
            logger.info(f"No files found in the input text. {text}")
            # raise ValueError("No files found in the input text.")
        
        return files, files_content
    
    
    def parse_json(self, text:str) -> Dict:
        """
        Parse the input text and extract json details.

        Args:
            text (str): The input text containing json.

        Returns:
            Dict: A json object containing json details.
        """
        
        text = "{".join(text.split("{")[1:])
        text = "}".join(text.split("}")[:-1])
        return json.loads(f"{{{text}}}")
