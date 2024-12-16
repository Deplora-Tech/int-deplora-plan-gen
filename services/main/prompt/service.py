import requests, json

from services.main.communication.models import MessageRequest


class PromptService:
    def prepare_prompt(self, request: MessageRequest):
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
            projectDataR.raise_for_status()
            projectData = projectDataR.json().get("deployment_info_after_refinement", {})
        except requests.exceptions.RequestException as e:
            print(f"Error fetching deployment info: {e}")
            projectData = {}

        try:
            # Fetch user preferences
            preferencesR = requests.get(preferences_url, params=preferences_params)
            preferencesR.raise_for_status()
            preferences = preferencesR.json().get("data", {})
        except requests.exceptions.RequestException as e:
            print(f"Error fetching preferences: {e}")
            preferences = {}

        prompt = f'''
        You are a highly capable deployment planner with expertise in creating optimal deployment strategies for web applications. 
        Using the provided project information, user preferences, and any additional context, generate a **detailed deployment plan** 
        and produce the necessary **configuration files** and artifacts.

        ### Inputs:
        **Project Data:**
        {json.dumps(projectData, indent=4)}

        **User Preferences:**
        {json.dumps(preferences, indent=4)}

        **Prompt Context:** {request.message}

        ### Deliverables:
        - **Deployment Strategy**:
            - Identify the most suitable infrastructure (e.g., cloud services, compute resources, storage).
            - Specify orchestration, monitoring, and logging tools.
            - Provide a detailed plan to align with user preferences and leverage industry best practices.

        - **Configuration Artifacts**:
            - **Dockerfiles**:
                - Base image selection and environment configuration.
                - Multi-stage builds for production readiness.
            - **Kubernetes Manifests**:
                - Deployment YAMLs, Service definitions, and Ingress configurations.
            - **CI/CD Pipelines**:
                - YAML configurations for GitHub Actions, Jenkins, or GitLab CI for automated builds and deployments.
            - **Terraform or CloudFormation Templates**:
                - Define infrastructure-as-code for cloud resource provisioning.

        - **Implementation Steps**:
            - Step-by-step instructions for deploying the application.
            - Include commands for environment setup, package installation, and production builds.

        - **Build and Deployment Artifacts**:
            - Provide build commands and optimized production artifacts.
            - Example: Webpack/Vite configurations, compiled TypeScript files.

        - **Best Practices**:
            - Security configurations (e.g., managing secrets, SSL/TLS, API security).
            - Performance optimizations (e.g., caching strategies, load balancing).
            - Reliability measures (e.g., health checks, failover strategies).

        - **Scaling and Monitoring**:
            - Strategies for scaling applications, load balancing configurations (e.g., NGINX, HAProxy).
            - Monitoring and logging setups (e.g., Prometheus, Grafana, ELK Stack).

        - **Database and Backup Configurations**:
            - Migration scripts for database schema updates using Sequelize or TypeORM.
            - Backup and disaster recovery configurations.

        - **Rollback Strategy**:
            - Define rollback mechanisms (e.g., blue-green deployments, canary releases).
            - Provide IaC files for rolling back infrastructure changes.

        ### Note:
        - Ensure the deployment plan is concise, actionable, and adaptable to different environments (e.g., staging, production).
        - Include sample configurations or templates wherever applicable.
        - Use Markdown formatting for readability.

        ### Example Output:
        - Dockerfile:
            ```
            FROM node:14
            WORKDIR /app
            COPY package.json yarn.lock ./
            RUN yarn install
            COPY . .
            CMD ["yarn", "start"]
            ```

        - Kubernetes Deployment YAML:
            ```
            apiVersion: apps/v1
            kind: Deployment
            metadata:
              name: web-app
            spec:
              replicas: 3
              selector:
                matchLabels:
                  app: web-app
              template:
                metadata:
                  labels:
                    app: web-app
                spec:
                  containers:
                  - name: web-app
                    image: web-app:latest
                    ports:
                    - containerPort: 3000
            ```
        '''

        return prompt

    def prepare_conversation_prompt(self, request: MessageRequest):
        prompt = f'''
        You are Deplora AI assistant, a chatbot designed to assist users with deployment-related queries.
        Based on the conversation, generate a suitable response, and provide any additional information or context as needed.
        
        input: {request.message}
        chat history: {request.chat_history}
        
        output:
        '''
        return prompt
