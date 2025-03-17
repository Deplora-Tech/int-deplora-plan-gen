preferences = {
            "positive_preferences": [
                ["CloudProvider", "Azure", 0.81809013001114, "High"],
                ["ObjectStorageService", "S3", 0.6786340000000001, "Low"],
                ["ComputeService", "Lambda", 0.6722666666666667, "Low"],
                ["IdentityAndAccessManagementService", "IAM", 0.6571, "Low"],
                ["DatabaseService", "RDS", 0.649, "Low"],
                ["ContainerOrchestrationPlatform", "ECS", 0.64, "Low"],
                ["OtherService", "VPC", 0.64, "Low"],
                ["MessageQueueService", "Pub/Sub", 0.63, "Low"],
                ["NoSQLDatabaseService", "Firestore", 0.63, "Low"],
                ["ContentDeliveryNetwork", "CloudFront", 0.626, "Low"],
                ["MonitoringService", "CloudWatch", 0.61, "Low"],
            ],
            "negative_preferences": [],
        }

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

user_prompt = "Deploy this to aws using docker"
chat_history = []