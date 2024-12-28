import os
import subprocess
import json
import requests

class ValidatorService:
    def __init__(self, base_path, jenkins_url, jenkins_user, jenkins_token):
        self.base_path = base_path
        self.jenkins_url = jenkins_url
        self.jenkins_user = jenkins_user
        self.jenkins_token = jenkins_token

    def validate_terraform(self):
        terraform_path = os.path.join(self.base_path, "inputs", "terraform")
        try:
            result = subprocess.run([
                "terraform", "validate"
            ], cwd=terraform_path, capture_output=True, text=True)

            if result.returncode == 0:
                return {"status": "valid", "message": "Terraform files are valid."}
            else:
                return {"status": "invalid", "message": result.stderr}
        except FileNotFoundError:
            return {"status": "error", "message": "Terraform CLI not found."}

    def validate_docker_compose(self):
        docker_compose_file = os.path.join(self.base_path, "inputs", "docker-compose.yml")
        try:
            result = subprocess.run([
                "docker-compose", "config"
            ], cwd=os.path.dirname(docker_compose_file), capture_output=True, text=True)

            if result.returncode == 0:
                return {"status": "valid", "message": "docker-compose.yml is valid."}
            else:
                return {"status": "invalid", "message": result.stderr}
        except FileNotFoundError:
            return {"status": "error", "message": "docker-compose CLI not found."}

    def validate_dockerfile(self):
        dockerfile_path = os.path.join(self.base_path, "inputs", "Dockerfile")
        try:
            result = subprocess.run([
                "docker", "build", "-t", "test-image", "-f", dockerfile_path, "."
            ], cwd=os.path.dirname(dockerfile_path), capture_output=True, text=True)

            if result.returncode == 0:
                return {"status": "valid", "message": "Dockerfile is valid."}
            else:
                return {"status": "invalid", "message": result.stderr}
        except FileNotFoundError:
            return {"status": "error", "message": "Docker CLI not found."}

    def validate_jenkinsfile(self):
        jenkinsfile_path = os.path.join(self.base_path, "inputs", "Jenkinsfile")
        if not os.path.exists(jenkinsfile_path):
            return {"status": "invalid", "message": "Jenkinsfile not found."}

        with open(jenkinsfile_path, "r") as file:
            jenkinsfile_content = file.read()

        url = f"{self.jenkins_url}/pipeline-model-converter/validate"
        auth = (self.jenkins_user, self.jenkins_token)

        try:
            response = requests.post(url, auth=auth, data={"jenkinsfile": jenkinsfile_content})
            if response.status_code == 200:
                return {"status": "valid", "message": "Jenkinsfile is valid."}
            else:
                return {"status": "invalid", "message": response.text}
        except requests.RequestException as e:
            return {"status": "error", "message": str(e)}

    def validate_all(self):
        results = {
            "terraform": self.validate_terraform(),
            "docker_compose": self.validate_docker_compose(),
            "dockerfile": self.validate_dockerfile(),
            "jenkinsfile": self.validate_jenkinsfile()
        }
        return results

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    jenkins_url = "http://localhost:8080"
    jenkins_user = "your_username"
    jenkins_token = "your_api_token"

    validator = ValidatorService(base_path, jenkins_url, jenkins_user, jenkins_token)
    results = validator.validate_all()

    print(json.dumps(results, indent=4))
