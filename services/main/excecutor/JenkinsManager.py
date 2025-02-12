import requests
import os, time, re
from dotenv import load_dotenv
from bs4 import BeautifulSoup


class JenkinsManager:
    def __init__(self):
        load_dotenv()
        self.jenkins_url = os.getenv("JENKINS_URL")
        self.username = os.getenv("JENKINS_USERNAME")
        self.api_token = os.getenv("JENKINS_API_TOKEN")

    def create_folder(self, folder_name):
        url = f"{self.jenkins_url}/createItem?name={folder_name}"
        headers = {"Content-Type": "application/xml"}
        folder_config = f"""
        <com.cloudbees.hudson.plugins.folder.Folder plugin="cloudbees-folder@6.15">
            <description>Folder for {folder_name}</description>
        </com.cloudbees.hudson.plugins.folder.Folder>
        """
        response = requests.post(
            url,
            auth=(self.username, self.api_token),
            headers=headers,
            data=folder_config,
        )

        if response.status_code == 200:
            print(f"Folder '{folder_name}' created successfully.")
        elif response.status_code == 400 and "already exists" in response.text:
            print(f"Folder '{folder_name}' already exists.")
        else:
            print(f"Failed to create folder '{folder_name}': {self._parse_error_text(response)}")
    
    def _read_jenkinsfile(self, local_directory_path):
        jenkinsfile_path = f"{local_directory_path}/Jenkinsfile"
        with open(jenkinsfile_path, "r") as file:
            return file.read()

    def create_local_pipeline(self, folder_name, pipeline_name, local_directory_path):
        jenkinsfile_content = self._read_jenkinsfile(local_directory_path)

        url = f"{self.jenkins_url}/job/{folder_name}/createItem?name={pipeline_name}"
        headers = {"Content-Type": "application/xml"}
        pipeline_config = f"""
        <flow-definition plugin="workflow-job@2.42">
            <description>Pipeline for {pipeline_name} running from local directory</description>
            <keepDependencies>false</keepDependencies>
            <properties/>
            <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2.92">
                <script>
                    {jenkinsfile_content}
                </script>
                <sandbox>true</sandbox>
            </definition>
            <triggers/>
            <disabled>false</disabled>
        </flow-definition>
        """
        response = requests.post(
            url,
            auth=(self.username, self.api_token),
            headers=headers,
            data=pipeline_config,
        )

        if response.status_code == 200:
            print(
                f"Pipeline '{pipeline_name}' created successfully inside '{folder_name}'."
            )
        elif response.status_code == 400 and "already exists" in response.text:
            print(f"Pipeline '{pipeline_name}' already exists inside '{folder_name}'.")
            self.delete_pipeline(folder_name, pipeline_name)
            self.create_local_pipeline(folder_name, pipeline_name, local_directory_path)
            
        else:
            print(f"Failed to create pipeline '{pipeline_name}': {self._parse_error_text(response)}")

    def delete_pipeline(self, folder_name, pipeline_name):
        url = f"{self.jenkins_url}/job/{folder_name}/job/{pipeline_name}/doDelete"
        response = requests.post(url, auth=(self.username, self.api_token))

        if response.status_code == 200:
            print(
                f"Pipeline '{pipeline_name}' in folder '{folder_name}' deleted successfully."
            )
        elif response.status_code == 404:
            print(f"Pipeline '{pipeline_name}' not found in folder '{folder_name}'.")
        else:
            print(
                f"Failed to delete pipeline '{pipeline_name}': {response.status_code} - {self._parse_error_text(response)}"
            )

    def trigger_pipeline_build(self, folder_name, pipeline_name):
        last_build_id = "0"

        try:
            last_build_id = self.monitor_build_status(folder_name, pipeline_name, "lastBuild")["id"]
        except Exception:
            pass

        new_build_id = int(last_build_id) + 1

        build_url = f"{self.jenkins_url}/job/{folder_name}/job/{pipeline_name}/build"
        response = requests.post(build_url, auth=(self.username, self.api_token))

        if response.status_code == 201:
            print(f"Build triggered successfully for pipeline '{pipeline_name}'.")
            time.sleep(10)
            return new_build_id
        else:
            print(
                f"Failed to trigger build for pipeline '{pipeline_name}': {self._parse_error_text(response)}"
            )
            return None

    def monitor_build_status(self, folder_name, pipeline_name, build_id):
        queue_url = f"{self.jenkins_url}/job/{folder_name}/job/{pipeline_name}/{build_id}/api/json"

        response = requests.get(queue_url, auth=(self.username, self.api_token))
        if response.status_code == 200:
            build_info = response.json()
            
            result = {
                "id": build_info.get("id"),
                "estimatedDuration": build_info.get("estimatedDuration"),
                "timestamp": build_info.get("timestamp"),
                # "url": build_info.get("url"),
                "duration": build_info.get("duration"),
                "building": build_info.get("building"),
            }

            return result
        else:
            
            raise Exception(f"Failed to monitor build status: Received response {self._parse_error_text(response)}")

    def get_stages_info(self, folder_name, pipeline_name, build_id):
        stages_url = f"{self.jenkins_url}/job/{folder_name}/job/{pipeline_name}/{build_id}/wfapi/describe"
        response = requests.get(stages_url, auth=(self.username, self.api_token))
        if response.status_code == 200:
            stages_info = response.json()["stages"]
            stages_info = [
                {
                    "name": stage["name"],
                    "status": stage["status"],
                    "durationMillis": stage["durationMillis"],
                    "id": stage["id"],
                }
                for stage in stages_info
            ]

            is_building = self.monitor_build_status(folder_name, pipeline_name, build_id)["building"]

            return stages_info, is_building

    def fetch_console_output(self, folder_name, pipeline_name, build_id):
        console_url = f"{self.jenkins_url}/job/{folder_name}/job/{pipeline_name}/{build_id}/consoleText"

        try:
            response = requests.get(console_url, auth=(self.username, self.api_token))
            if response.status_code == 200:
                print(response.text)
            else:
                print(f"Error fetching console output: {self._parse_error_text(response)}")
        except KeyboardInterrupt:
            print("Console output fetching stopped.")

    def list_jenkins_builds(self, folder_name, pipeline_name,):
        url = f"{self.jenkins_url}/job/{folder_name}/job/{pipeline_name}/api/json"
        response = requests.get(url, auth=(self.username, self.api_token))
        if response.status_code == 200:
            builds = response.json()
            return builds
        else:
            print(f"Failed to list builds: {self._parse_error_text(response)}")
            return None     

    def _parse_error_text(self, response):
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.get_text(strip=True) 
        
        except Exception:
            return "Failed to parse the error"
    
    def list_stages(self, local_directory_path):
        """
        Extracts stage names from a Jenkinsfile text.
        
        This regex looks for patterns like:
        stage('Stage Name')
        stage("Stage Name")
        """
        jenkinsfile_text = self._read_jenkinsfile(local_directory_path)
        # Regular expression to capture the stage name inside single or double quotes
        stage_pattern = r'stage\s*\(\s*[\'"](.+?)[\'"]\s*\)'
        return re.findall(stage_pattern, jenkinsfile_text)

    def get_logs_for_stage(self, folder_name, pipeline_name, build_id, stage_id):
        stages_url = f"{self.jenkins_url}/job/{folder_name}/job/{pipeline_name}/{build_id}/pipeline-console/log?nodeId={stage_id}"
        response = requests.get(stages_url, auth=(self.username, self.api_token))

        if response.status_code == 200:
            return response.text
        else:
            return f"Failed to fetch logs for stage {stage_id}: {self._parse_error_text(response)}"
        
 