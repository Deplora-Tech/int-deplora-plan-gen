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
            preferences = preferencesR.json().get("data", {})
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
        "The plan should cover the following aspects:\n\n"
            "1. **Tech Stack and Environment Setup**: Specify the required tech stack, including Node.js version, npm/yarn, "
            "and other relevant tools like Docker, database systems (e.g., MongoDB, PostgreSQL), and any front-end frameworks (e.g., React, Angular). "
            "Include OS configurations and environment variables setup.\n\n"
            "2. **Build and Artifacts**: Provide steps to generate build artifacts, including compiling TypeScript (if used), bundling code using Webpack or Vite, "
            "and optimizing the output for production.\n\n"
            "3. **Dependency Management**: Ensure proper installation of all project dependencies with npm or yarn, along with handling compatibility issues.\n\n"
            "4. **CI/CD Pipeline**: Describe the configuration of a continuous integration and deployment pipeline. Include tools like GitHub Actions, GitLab CI, Jenkins, or CircleCI. "
            "Outline steps for testing, building, and deploying.\n\n"
            "5. **Security Best Practices**: Include steps to manage secrets securely using tools like dotenv, AWS Secrets Manager, or HashiCorp Vault. "
            "Incorporate practices to secure APIs, implement SSL/TLS certificates, and enable firewall configurations.\n\n"
            "6. **Hosting and Deployment**: Provide detailed instructions for deploying to cloud platforms such as AWS, Azure, Google Cloud, or platforms like Heroku, Netlify, or Vercel. "
            "Include containerization using Docker and orchestrations with Kubernetes if applicable.\n\n"
            "7. **Scaling and Load Balancing**: Include strategies for scaling the application, load balancing with tools like NGINX, HAProxy, or AWS Elastic Load Balancer, "
            "and setting up auto-scaling groups.\n\n"
            "8. **Monitoring and Logging**: Recommend monitoring tools like Prometheus, Grafana, and logging systems like ELK stack or Datadog. "
            "Provide steps for implementing alerts and health checks.\n\n"
            "9. **Database Migration and Management**: Detail database setup, schema migrations using tools like Sequelize, TypeORM, or Knex, and backups.\n\n"
            "10. **Rollback Strategy**: Include a rollback plan in case of deployment failure, detailing version control, blue-green deployments, and canary releases.\n\n"

        '''
        
        return prompt