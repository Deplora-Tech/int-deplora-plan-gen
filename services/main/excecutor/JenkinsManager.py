import requests
import os, time, re, json
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

class JenkinsManager:
    def __init__(self):
        load_dotenv(override=True)
        self.jenkins_url = os.getenv("JENKINS_URL").strip().strip('"').strip("'")

        self.username = os.getenv("JENKINS_USERNAME")
        self.api_token = os.getenv("JENKINS_API_TOKEN")
    
        print("Jenkins URL:", self.jenkins_url)

    def set_folder_env_variable( self, folder_name, var_name, var_value):
        """
        Sets an environment variable for a specific folder in Jenkins using REST API.

        Args:
            jenkins_url (str): Base URL of your Jenkins instance.
            folder_path (str): Path to your folder, e.g., "my-folder" or "folder1/folder2".
            var_name (str): Environment variable name.
            var_value (str): Environment variable value.
            username (str): Jenkins username.
            api_token (str): Jenkins user API token/password.

        Returns:
            bool: True if successfully updated, False otherwise.
        """

        config_url = f"{self.jenkins_url}/job/{folder_name}/config.xml"

        # Get current configuration
        response = requests.get(config_url, auth=(self.username, self.api_token))

        if response.status_code != 200:
            print("Failed to retrieve config.xml", response.status_code, response.text)
            return False

        # Parse XML
        root = ET.fromstring(response.text)

        # Namespace fix
        ns = {'jenkins': 'http://maven.apache.org/POM/4.0.0'}

        # Check if folder-properties exists; create if not
        properties = root.find('properties')
        if properties is None:
            properties = ET.SubElement(root, 'properties')

        folder_properties = properties.find('com.mig82.folders.properties.FolderProperties')
        if folder_properties is None:
            folder_properties = ET.SubElement(properties, 'com.mig82.folders.properties.FolderProperties')
            env_vars = ET.SubElement(folder_properties, 'properties')
        else:
            env_vars = folder_properties.find('properties')
            if env_vars is None:
                env_vars = ET.SubElement(folder_properties, 'properties')

        # Add or update environment variable
        new_var = ET.SubElement(env_vars, 'com.mig82.folders.properties.StringProperty')
        key_elem = ET.SubElement(new_var, 'key')
        key_elem.text = var_name
        value_elem = ET.SubElement(new_var, 'value')
        value_elem.text = var_value

        # Convert XML back to string
        updated_config_xml = ET.tostring(root, encoding='utf-8').decode('utf-8')

        # POST updated configuration back to Jenkins
        headers = {'Content-Type': 'application/xml'}
        update_response = requests.post(config_url, data=updated_config_xml, auth=(self.username, self.api_token), headers=headers)

        if update_response.status_code == 200:
            print("Folder environment variable updated successfully!")
            return True
        else:
            print("Failed to update config.xml", update_response.status_code, update_response.text)
            return False
    
    def create_jenkins_secret_text(self, folder_name, credential_id, secret_text, description=""):

        url = f"{self.jenkins_url}/job/{folder_name}/credentials/store/folder/domain/_/createCredentials"

        xml_payload = f"""
        <org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl>
            <scope>FOLDER</scope>
            <id>{credential_id}</id>
            <description>{description}</description>
            <secret>{secret_text}</secret>
        </org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl>
        """

        headers = {
            "Content-Type": "application/xml"
        }

        response = requests.post(url, auth=(self.username, self.api_token), headers=headers, data=xml_payload)

        if response.status_code == 200:
            return {"status": "success", "message": "Secret text credential created successfully"}
        else:
            return {"status": "error", "message": f"Failed to create credential: {self._parse_error_text(response)}"}



    def create_project_folder(self, organization, folder_name, clone_path):
        url = f"{self.jenkins_url}/job/{organization}/createItem?name={folder_name}"
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
            self.set_folder_env_variable(f"{organization}/job/{folder_name}", "CLONE_PATH", clone_path)
            print(f"Folder '{folder_name}' created successfully.")
        elif response.status_code == 400 and "already exists" in response.text:
            print(f"Folder '{folder_name}' already exists.")
        else:
            print(f"Failed to create folder '{folder_name}': {self._parse_error_text(response)}")
    

    def create_org_folder(self, folder_name):
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
            self.create_jenkins_secret_text(folder_name, "aws-access-key-id", "", "AWS Access Key ID")
            self.create_jenkins_secret_text(folder_name, "aws-secret-access-key", "", "AWS Secret Access Key")
            
            self.set_folder_env_variable(folder_name, "AWS_REGION", "us-east-1")
            self.set_folder_env_variable(folder_name, "AWS_ACCOUNT_ID", "123")
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
        # local_directory_path = "/home/sahiru/deplora/repo-clones/d114e906-957a-428f-b1af-6c47bb6577c4/po-server"
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
        # Escape special characters in the XML
        pipeline_config = pipeline_config.replace("&", "&amp;")
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
            print(f"Pipeline '{pipeline_name}' already exists inside '{folder_name}'. Updating the pipeline script.")
            update_url = f"{self.jenkins_url}/job/{folder_name}/job/{pipeline_name}/config.xml"
            update_response = requests.post(
                update_url,
                auth=(self.username, self.api_token),
                headers=headers,
                data=pipeline_config,
            )
            if update_response.status_code == 200:
                print(f"Pipeline '{pipeline_name}' updated successfully inside '{folder_name}'.")
            else:
                print(f"Failed to update pipeline '{pipeline_name}': {self._parse_error_text(update_response)}")
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
    
    def stop_pipeline_build(self, folder_name, pipeline_name, build_id):
        stop_url = f"{self.jenkins_url}/job/{folder_name}/job/{pipeline_name}/{build_id}/stop"
        response = requests.post(stop_url, auth=(self.username, self.api_token))

        if response.status_code == 200:
            print(f"Build {build_id} stopped successfully for pipeline '{pipeline_name}'.")
        else:
            print(f"Failed to stop build {build_id} for pipeline '{pipeline_name}': {self._parse_error_text(response)}")

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
                return response.text
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
        stages_url = f"{self.jenkins_url}/job/{folder_name}/job/{pipeline_name}/{build_id}/pipeline-overview/log?nodeId={stage_id}"
        response = requests.get(stages_url, auth=(self.username, self.api_token))

        if response.status_code == 200:
            return response.text
        else:
            return f"Failed to fetch logs for stage {stage_id}: {self._parse_error_text(response)}"

        
 