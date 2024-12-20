from core.logger import logger
from services.main.communication.models import MessageRequest
from services.main.validationManager.service import ValidationService
from services.main.planGenerator.service import PlanGeneratorService
from services.main.repoManager.service import RepoService
from services.main.workers.llm_worker import LLMService
from services.main.utils.FileParser import FileParser
import asyncio


class ManagementService:
    def __init__(self):
        self.validation_service = ValidationService(
            "C:\\Users\\Asus\\Downloads\\testtt02\\validate"
        )
        self.repo_service = RepoService("C:\\Users\\Asus\\Downloads\\testtt02\\repos")
        self.plan_generator_service = PlanGeneratorService()
        self.llm_service = LLMService()
        self.file_parser = FileParser()

    async def generate_deployment_plan(
        self,
        prompt: str,
        project_id: str,
        organization_id: str,
        user_id: str,
        chat_history: dict,
        session_id: str,
    ) -> dict:
        """
        Generate a deployment plan based on the request
        1. Initialize the Repo
        2. Prepare the prompt
        3. Call Plan Generator Service
        4. Call Validation Service
        IF validation pass:
            5. Call Repo Service to commit new files
        ELSE:
            5. Call Prompt serrvice to prepare fixing prompt
            GOTO 3
        """

        git_url = "https://github.com/sahiruw/po-server"
        repo_task = self.repo_service.clone_repo(
            repo_url=git_url, branch="main", session_id=session_id
        )

        preferences_task = self.retrieve_preferences(
            prompt=prompt,
            project_id=project_id,
            organization_id=organization_id,
            user_id=user_id,
            chat_history=chat_history,
        )

        project_details_task = self.retrieve_project_details(project_id)

        repo, user_preferences, project_details = await asyncio.gather(
            repo_task, preferences_task, project_details_task
        )

        deployment_recommendation, deployment_solution = (
            await self.plan_generator_service.generate_deployment_plan(
                prompt=prompt,
                user_preferences=user_preferences,
                project_details=project_details,
                chat_history=chat_history,
            )
        )

        logger.info(
            
            f"Generating deployment plan for project {project_id} in organization {organization_id} for user {user_id}",
        )
        
        logger.info(f"Deployment recommendation: {deployment_recommendation}")
        logger.info(f"Deployment solution: {deployment_solution}")
        
        parsed_files = self.file_parser.parse(deployment_solution)

        logger.info(f"Files to be committed: {len(parsed_files)}")
        
        print(deployment_solution)
        
        for file in parsed_files:
            print(f"File: {file.get('file_name')} Type: {file.get('type')} Path: {file.get('path')}")

    async def process_conversation(self, request: MessageRequest) -> dict:
        prompt = self.prompt_service.prepare_conversation_prompt(request)
        return await self.llm_service.llm_request(prompt)

    async def retrieve_preferences(
        self,
        prompt: str,
        project_id: str,
        organization_id: str,
        user_id: str,
        chat_history: dict,
    ) -> dict:
        logger.debug("Retrieving user preferences...")
        preferences = {
            "positive_preferences": [
                ["MonitoringTool", "Stackdriver", 0.649, "Low"],
                [
                    "CloudStorageService",
                    "Cloud Storage bucket",
                    0.6446666666666666,
                    "Low",
                ],
                ["MonitoringService", "CloudWatch", 0.64, "Low"],
                ["ContainerOrchestrationService", "ECS", 0.64, "Low"],
                ["ScalabilityFeature", "autoscaling", 0.64, "Low"],
                ["CloudService", "Compute Engine", 0.64, "Low"],
                ["StorageService", "S3 bucket", 0.63055, "Low"],
                ["AccessControl", "IAM role", 0.63, "Low"],
                ["ScalingFeature", "autoscaling", 0.63, "Low"],
                ["StoragePolicy", "lifecycle policies", 0.63, "Low"],
                ["NetworkingConfiguration", "Route tables", 0.62, "Low"],
                ["Application", "application", 0.619, "Low"],
                ["InMemoryDataStore", "Memorystore", 0.6133333333333333, "Low"],
                ["ServerlessCompute", "Cloud Functions", 0.6, "Low"],
                ["ServerlessComputeService", "Cloud Functions", 0.6, "Low"],
                ["AccessControlPolicy", "bucket policy", 0.6, "Low"],
                ["IdentityAccessManagement", "IAM policies", 0.6, "Low"],
                ["DatabaseManagementSystem", "RDS Postgres database", 0.6, "Low"],
                ["SecurityFeature", "encryption policies", 0.6, "Low"],
                ["SecurityPolicy", "strong password policies", 0.6, "Low"],
                ["DisasterRecoveryFeature", "automated backups", 0.6, "Low"],
                ["PerformanceMetric", "end-to-end latency", 0.6, "Low"],
                ["ContentDeliveryNetwork", "Cloud CDN", 0.6, "Low"],
                ["SecurityProtocol", "two-step verification", 0.6, "Low"],
                ["ErrorHandlingMechanism", "error handling", 0.6, "Low"],
                ["ComputeResource", "worker nodes", 0.6, "Low"],
                ["LoggingMechanism", "execution logs", 0.6, "Low"],
                ["TracingConfiguration", "segment sampling", 0.6, "Low"],
                ["CacheConfiguration", "cache settings", 0.6, "Low"],
                ["CacheManagement", "cache invalidation", 0.6, "Low"],
                ["VirtualPrivateCloud", "VPCs", 0.6, "Low"],
                ["Protocol", "HTTP/2", 0.6, "Low"],
                ["LogData", "function logs", 0.6, "Low"],
                ["MessageQueue", "Pub/Sub", 0.6, "Low"],
                ["EventDrivenArchitecture", "EventBridge", 0.6, "Low"],
                ["SecurityConfiguration", "security groups", 0.6, "Low"],
                ["ContainerPlatform", "GKE", 0.6, "Low"],
                ["UserGroup", "stakeholders", 0.6, "Low"],
                ["Permission", "public read access", 0.6, "Low"],
                ["DataWarehouse", "BigQuery", 0.6, "Low"],
                ["NotificationSystem", "alerts", 0.6, "Low"],
                ["PerformanceOptimization", "caching policies", 0.6, "Low"],
                ["ContainerOrchestrationPlatform", "GKE cluster", 0.6, "Low"],
                ["SecurityService", "Cloud Armor", 0.6, "Low"],
                ["BigDataFramework", "Hadoop", 0.6, "Low"],
                ["MonitoringFeature", "Cluster monitoring", 0.6, "Low"],
                ["PerformanceIndicator", "performance metrics", 0.6, "Low"],
                ["VisualizationTool", "Dashboards", 0.6, "Low"],
                ["BusinessIntelligenceTool", "Data Studio", 0.6, "Low"],
                ["CostMetric", "storage costs", 0.6, "Low"],
                ["AccessLevel", "Viewer permissions", 0.6, "Low"],
                ["APIManagementService", "API Gateway", 0.6, "Low"],
                ["TracingService", "X-Ray", 0.6, "Low"],
                ["OriginServer", "origin server", 0.6, "Low"],
                ["Encryption", "encryption keys", 0.6, "Low"],
                ["CompliancePolicy", "Company policies", 0.6, "Low"],
                ["ResourceAllocation", "allocated memory", 0.6, "Low"],
                ["BackupFeature", "Object Versioning", 0.6, "Low"],
                ["QueryOptimizationTechnique", "caching", 0.6, "Low"],
                ["MonitoringData", "logs", 0.6, "Low"],
                ["DataVisualization", "custom charts", 0.6, "Low"],
                ["WorkflowAutomationTool", "state machine", 0.6, "Low"],
                ["DataProcessing", "ETL processing", 0.6, "Low"],
            ],
            "negative_preferences": [
                ["ServerlessFunction", "Lambda function", 0.4, "Low"],
                ["DataClassification", "sensitive data", 0.4, "Low"],
                ["ErrorCondition", "Node failures", 0.4, "Low"],
                ["SecurityRisk", "vulnerabilities", 0.4, "Low"],
                ["ContentType", "frequently updated content", 0.4, "Low"],
                ["AssetClassification", "high-risk assets", 0.4, "Low"],
            ],
        }

        # await asyncio.sleep(2)
        return preferences

    async def retrieve_project_details(self, project_id: str) -> dict:
        logger.debug("Retrieving project details...")

        project_data = {
            "application": {
                "name": "React Application",
                "type": ["Web Application", "ReactJS", "React"],
                "description": "A Simple ReactJS Project",
                "dependencies": [
                    {
                        "name": "React",
                        "version": "x.x.x",
                    },
                    "react-router-dom",
                    "react-bootstrap",
                    "axios",
                ],
                "language": ["JavaScript"],
                "framework": ["ReactJS"],
                "architecture": ["Single-page application", "Client-Server"],
            },
            "environment": {"runtime": ["Node.js"]},
        }

        # await asyncio.sleep(3)
        return project_data
