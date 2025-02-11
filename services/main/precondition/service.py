import os
import subprocess
import shutil
from typing import Optional, Dict
from git import Repo
from core.logger import logger
from logging.handlers import RotatingFileHandler
import stat
import re


def remove_readonly(func, path, excinfo):
    """Clear the read-only attribute and retry."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


class TestCoverageService:
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.test_commands = {
            "Python": {
                "pytest": "pytest --cov=.",
                "unittest": "coverage run -m unittest discover && coverage report",
            },
            "JavaScript": {"jest": "jest --coverage", "mocha": "nyc mocha"},
            "TypeScript": {"jest": "jest --coverage", "mocha": "nyc mocha"},
            "Java": {"junit": "mvn clean test", "jacoco": "mvn jacoco:report"},
            "Go": {"go test": "go test -cover ./..."},
            "Ruby": {"rspec": "rspec --format documentation --coverage"},
            "PHP": {"phpunit": "phpunit --coverage-text"},
            "C#": {"dotnet": "dotnet test /p:CollectCoverage=true"},
        }

    def detect_testing_tool(self, repo_path: str, language: str) -> Optional[str]:

        if language == "Python":
            if os.path.exists(os.path.join(repo_path, "requirements.txt")):
                with open(os.path.join(repo_path, "requirements.txt")) as f:
                    for line in f:
                        if "pytest" in line:
                            return "pytest"
                        if "unittest" in line:
                            return "unittest"

        if language in ["JavaScript", "TypeScript"]:
            if os.path.exists(os.path.join(repo_path, "package.json")):
                with open(os.path.join(repo_path, "package.json")) as f:
                    package_json = f.read()
                    if "jest" in package_json:
                        return "jest"
                    if "mocha" in package_json:
                        return "mocha"

        if language == "Java":
            if os.path.exists(os.path.join(repo_path, "pom.xml")):
                return "junit"
            if os.path.exists(os.path.join(repo_path, "build.gradle")):
                return "jacoco"

        if language == "Go":
            if os.path.exists(os.path.join(repo_path, "go.mod")):
                return "go test"

        if language == "Ruby":
            if os.path.exists(os.path.join(repo_path, "Gemfile")):
                return "rspec"

        if language == "PHP":
            if os.path.exists(os.path.join(repo_path, "composer.json")):
                return "phpunit"

        if language == "C#":
            if any(file.endswith(".csproj") for file in os.listdir(repo_path)):
                return "dotnet"

        return None

    def run_test_coverage(self, repo_path: str, language: str) -> Dict[str, str]:

        test_tool = self.detect_testing_tool(repo_path, language)
        if not test_tool:
            return {"error": f"No testing tool found for {language}"}

        command = self.test_commands.get(language, {}).get(test_tool)
        if not command:
            return {"error": f"No test command found for {test_tool}"}

        try:
            result = subprocess.run(
                command, shell=True, cwd=repo_path, capture_output=True, text=True
            )
            output = result.stdout + result.stderr
            coverage = "N/A"

            if language in ["Python", "JavaScript", "TypeScript", "Ruby", "PHP", "Go"]:
                match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
                if not match:
                    match = re.search(r"Coverage\s*:\s*(\d+)%", output)
                if match:
                    coverage = match.group(1)

            elif language == "Java" and test_tool == "jacoco":
                jacoco_report = os.path.join(repo_path, "target/site/jacoco/index.html")
                if os.path.exists(jacoco_report):
                    with open(jacoco_report, "r", encoding="utf-8") as f:
                        html_content = f.read()
                        match = re.search(r"Coverage:.*?(\d+)%", html_content)
                        if match:
                            coverage = match.group(1)

            elif language == "C#" and test_tool == "dotnet":
                coverage_report = os.path.join(repo_path, "TestResults/Coverage.xml")
                if os.path.exists(coverage_report):
                    with open(coverage_report, "r", encoding="utf-8") as f:
                        xml_content = f.read()
                        match = re.search(r'line-rate="(\d+\.\d+)"', xml_content)
                        if match:
                            coverage = str(round(float(match.group(1)) * 100))

            return {
                "language": language,
                "test_tool": test_tool,
                "coverage": f"{coverage}%",
            }

        except Exception as e:
            return {"error": str(e)}

    def analyze_repo(self, repo_url: str, session_id: str, language: str = "Python"):
        """
        Clones the repo and runs test coverage analysis.
        """
        repo_path = os.path.join(
            self.root_path, session_id, repo_url.split("/")[-1].replace(".git", "")
        )
        try:

            # Remove the repo path if it exists
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path, onerror=remove_readonly)

            logger.info(f"Cloning repository from {repo_url} to {repo_path}...")
            Repo.clone_from(repo_url, repo_path)
            logger.info("Repository cloned successfully.")

            return self.run_test_coverage(repo_path, language)

        except Exception as e:
            logger.error(f"Error analyzing repo: {e}")
            return {"error": str(e)}
