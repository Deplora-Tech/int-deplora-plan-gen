import requests
import os
from dotenv import load_dotenv


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
            print(f"Failed to create folder '{folder_name}': {response.text}")

    def create_local_pipeline(self, folder_name, pipeline_name, local_directory_path):
        jenkinsfile_content = open(f"{local_directory_path}/Jenkinsfile", "r").read()

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
        else:
            print(f"Failed to create pipeline '{pipeline_name}': {response.text}")

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
                f"Failed to delete pipeline '{pipeline_name}': {response.status_code} - {response.text}"
            )

    def trigger_pipeline_build(self, folder_name, pipeline_name):
        build_url = f"{self.jenkins_url}/job/{folder_name}/job/{pipeline_name}/build"
        response = requests.post(build_url, auth=(self.username, self.api_token))

        if response.status_code == 201:
            print(f"Build triggered successfully for pipeline '{pipeline_name}'.")

            return self.monitor_build_status(folder_name, pipeline_name, "lastBuild")
        else:
            print(
                f"Failed to trigger build for pipeline '{pipeline_name}': {response.text}"
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
                "url": build_info.get("url"),
                "duration": build_info.get("duration"),
                "building": build_info.get("building"),
            }

            return result
        else:
            raise Exception(f"Failed to monitor build status: {response.text}")

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
            return stages_info

    def fetch_console_output(self, build_url):
        console_url = f"{build_url}/consoleFull"
        try:
            response = requests.get(console_url, auth=(self.username, self.api_token))
            if response.status_code == 200:
                print(response.text)
            else:
                print(f"Error fetching console output: {response.text}")
        except KeyboardInterrupt:
            print("Console output fetching stopped.")


# Example usage
if __name__ == "__main__":
    jenkins = JenkinsManager(
        jenkins_url="http://localhost:8080/",
        username="Deplora",
        api_token="11834370adb99ae6692384941001094ff6",
    )

    folder_name = "OrganizationT"
    pipeline_name = "Project2"
    local_directory_path = "/mnt/c/Users/Asus/Downloads/testtt02/repos/123/po-server"

    jenkins.create_folder(folder_name)
    jenkins.delete_pipeline(folder_name, pipeline_name)
    jenkins.create_local_pipeline(folder_name, pipeline_name, local_directory_path)
    build_url = jenkins.trigger_pipeline_build(folder_name, pipeline_name)

    while True:
        jenkins.monitor_build_status(folder_name, pipeline_name)
