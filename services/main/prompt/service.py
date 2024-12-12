import requests, json

class PromptService:
    def prepare_prompt(self, client_id, project_id, raw_prompt, chat_history):
 
        client_id = "User 1"
        project_id = "Project 1"
        organization = "Org1"
        

        deployment_info_url = "http://192.168.110.7:8700/get-deployment-info/"
        preferences_url = "http://192.168.110.61:8000/search"

        # Define query parameters
        deployment_params = {
            "repo_url": "https://github.com/aditya-sridhar/simple-reactjs-app.git"
        }
        preferences_params = {
            "username": "User 3",
            "project": "Project 2",
            "organization": "Org2"
        }

        try:
            # Fetch deployment info
            projectDataR = requests.get(deployment_info_url, params=deployment_params)
            projectDataR.raise_for_status()  # Raise an error for HTTP errors
            projectData = projectDataR.json().get("deployment_info_after_refinement", {})
        except requests.exceptions.RequestException as e:
            print(f"Error fetching deployment info: {e}")
            projectData = {}

        try:
            # Fetch user preferences
            preferencesR = requests.get(preferences_url, params=preferences_params)
            preferencesR.raise_for_status()  # Raise an error for HTTP errors
            preferences = preferencesR.json().get("preferences", {})
        except requests.exceptions.RequestException as e:
            print(f"Error fetching preferences: {e}")
            preferences = {}

        # Print the results or proceed with your logic
        print("Deployment Info:", projectData)
        print("Preferences:", preferences)

        
        
        prompt = f'''
        You are a highly capable deployment planner with expertise in creating optimal deployment strategies for web applications. Using the provided project information, user preferences, and any additional context, generate a detailed deployment plan. The plan should align with the user’s preferences, leverage best practices, and include necessary configurations for a successful deployment.
        Inputs:
        Project Data:
        {json.dumps(projectData, indent=4)}
        User Preferences:
        {json.dumps(preferences, indent=4)}
        
        Prompt Context: {raw_prompt}
        
        Deliverables:
            Deployment Strategy: Identify the most suitable infrastructure (e.g., cloud services, compute resources, storage).
            Specify the orchestration, monitoring, and logging tools. Provide required configuration and Iac Files.
            
            Implementation Steps: Provide clear step-by-step instructions for deploying the application.
            
            Best Practices: Include tips for ensuring security, performance optimization, and reliability.
            
            Configuration Details: Key configurations for services, networks, databases, and other critical components.
            
            Considerations: Address challenges or trade-offs based on user preferences and project requirements.

        '''
        
        return prompt