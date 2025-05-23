import os
import json
from typing import List, Dict
from core.logger import logger


class FileParser:
    """
    A parser to identify, extract, and generate file objects from text containing <deploraFile> tags.
    """

    def __init__(self):
        """
        Initialize the parser with a base directory where files can be saved.
        """
        pass

    def parse(self, text: str) -> List[Dict[str, str]]:
        """
        Parse the input text and extract file details.

        Args:
            text (str): The input text containing <deploraFile> tags.

        Returns:
            List[Dict[str, str]]: A list of file objects containing file details.
        """
        files = []
        files_content = []

        # Start and end markers for the <deploraFile> tag
        file_start_tag = "<deploraFile"
        file_end_tag = "</deploraFile>"

        # Iterate over the text to find file blocks
        while file_start_tag in text:
            text = file_start_tag.join(text.split(file_start_tag)[1:])
 
            # Extract the file block and process it
            file_block = text.split(file_start_tag)[0]

            # Extract file type, filePath and action from the <deploraFile> tag
            file_type_start = file_block.find('type="') + len('type="')
            file_type_end = file_block.find('"', file_type_start)
            file_type = file_block[file_type_start:file_type_end]

            file_path_start = file_block.find('filePath="') + len('filePath="')
            file_path_end = file_block.find('"', file_path_start)
            file_path = file_block[file_path_start:file_path_end]

            file_action_start = file_block.find('action="') + len('action="')
            if file_action_start != -1:
                file_action_end = file_block.find('"', file_action_start)
                file_action = file_block[file_action_start:file_action_end]
            else:
                file_action = "create"

            # Extract content from between the tags
            file_content = ">".join(file_block.split(">")[1:]).split(file_end_tag)[0]

            # Clean up content (removing Markdown code blocks and CDATA)
            # Remove Markdown code blocks (```)
            file_content = self.remove_markdown_code_blocks(file_content)


            # Prepare the file object and append it to the result
            file_name = os.path.basename(file_path)
            file_object = {
                "file_name": file_name,
                "type": file_type,
                "path": file_path,
                "content": file_content,
                "action": file_action,
            }

            files.append(file_object)
            files_content.append(file_block)


        if len(files) == 0:
            raise ValueError("No files found in the input text.")

        return files, files_content
    
    @staticmethod
    def parse_json( text: str) -> Dict:
        """
        Parse the input text and extract json details.

        Args:
            text (str): The input text containing json.

        Returns:
            Dict: A json object containing json details.
        """
        # Clean up the text before parsing
        text = "{".join(text.split("{")[1:])
        text = "}".join(text.split("}")[:-1])

        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()
        return json.loads(f"{{{text}}}")
    
    def remove_markdown_code_blocks(self, content: str) -> str:
        """
        Removes Markdown code blocks from the content.

        Args:
            content (str): The content to remove code blocks from.

        Returns:
            str: The content with code blocks removed.
        """
        # Remove Markdown code blocks wrapped in triple backticks
        in_code_block = False
        result = []
        for line in content.split("\n"):
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue  # Skip the line with the opening or closing ```
            if not in_code_block:
                result.append(line)
        return "\n".join(result).strip()



if __name__ == "__main__":
    txtx = '''I will also include Terraform files for IaC and a Jenkinsfile for CI/CD.

**Assumptions:**

*   **AWS Credentials:** I assume AWS credentials are pre-configured in the Jenkins environment and Terraform environment via environment variables or IAM roles.
*   **Networking:** I assume a default VPC and subnet are available, or you will configure them separately.
*   **Application Port:** The React application will be served on port 80.
*   **Node.js Version:** Using the latest LTS version of Node.js in the Dockerfile.

```
<deploraFile type="Dockerfile" filePath="Dockerfile">
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the source code
COPY . .

# Build the app for production
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy the build output from the builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
</deploraFile>
```

```
<deploraFile type="terraform" filePath="terraform/main.tf">
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  required_version = ">= 1.0"
}

provider "aws" {
  region = var.aws_region
}

# Create an ECS cluster
resource "aws_ecs_cluster" "main" {
  name = var.cluster_name
}

# Create an ECR repository
resource "aws_ecr_repository" "main" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Define IAM role for ECS task execution
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
      },
    ],
  })
}

# Attach the necessary policies to the IAM role
resource "aws_iam_policy_attachment" "ecs_task_execution_policy_attachment" {
  name       = "ecs-task-execution-policy-attachment"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  roles      = [aws_iam_role.ecs_task_execution_role.name]
}

# Create Task Definition
resource "aws_ecs_task_definition" "main" {
  family             = var.task_definition_family
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  container_definitions = jsonencode([
    {
      name      = "react-app"
      image     = "${aws_ecr_repository.main.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ]
    }
  ])
}

# Create ECS Service
resource "aws_ecs_service" "main" {
  name            = var.service_name
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups = var.security_group_ids
    assign_public_ip = true
  }

  depends_on = [aws_iam_policy_attachment.ecs_task_execution_policy_attachment]
}

output "ecr_repository_url" {
  value = aws_ecr_repository.main.repository_url
}
</deploraFile>
```

```
<deploraFile type="terraform" filePath="terraform/variables.tf">
variable "aws_region" {
  type    = string
  default = "us-east-1"
  description = "AWS region to deploy to"
}

variable "cluster_name" {
  type    = string
  default = "react-app-cluster"
  description = "Name of the ECS cluster"
}

variable "ecr_repository_name" {
  type    = string
  default = "react-app-repo"
  description = "Name of the ECR repository"
}

variable "task_definition_family" {
  type    = string
  default = "react-app-task"
  description = "Family for the ECS task definition"
}

variable "task_cpu" {
  type    = string
  default = "256"
  description = "CPU units for the task"
}

variable "task_memory" {
  type    = string
  default = "512"
  description = "Memory for the task"
}

variable "service_name" {
  type    = string
  default = "react-app-service"
  description = "Name of the ECS service"
}

variable "desired_count" {
  type    = number
  default = 1
  description = "Desired number of tasks"
}

variable "subnet_ids" {
  type    = list(string)
  default = ["subnet-xxxxxxxxxxxxxxxxx"] # Replace with your subnet IDs
  description = "List of subnet IDs"
}

variable "security_group_ids" {
  type    = list(string)
  default = ["sg-xxxxxxxxxxxxxxxxx"] # Replace with your security group IDs
  description = "List of security group IDs"
}
</deploraFile>
```

```
<deploraFile type="terraform" filePath="terraform/terraform.tfvars">
aws_region = "us-east-1"
cluster_name = "my-react-cluster"
ecr_repository_name = "my-react-repo"
task_definition_family = "my-react-task"
task_cpu = "512"
task_memory = "1024"
service_name = "my-react-service"
desired_count = 2
subnet_ids = ["subnet-0bb1c79de3EXAMPLE", "subnet-0EXAMPLEe4b6bb"]
security_group_ids = ["sg-0e9EXAMPLE438b15"]
```

```
<deploraFile type="terraform" filePath="terraform/outputs.tf">
output "cluster_id" {
  value = aws_ecs_cluster.main.id
  description = "The ECS cluster ID"
}

output "service_name" {
  value = aws_ecs_service.main.name
  description = "The ECS service name"
}
```

```
<deploraFile type="Jenkinsfile" filePath="Jenkinsfile">
pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID     = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        AWS_DEFAULT_REGION    = 'us-east-1'
        ECR_REPOSITORY_URL  = '' // Will be populated by Terraform output
    }

    options {
        withFolderProperties()
    }

    stages {
        stage('Terraform Init') {
            steps {
                dir("${env.CLONE_PATH}/terraform") {
                    sh 'terraform init'
                }
            }
        }

        stage('Terraform Apply') {
            steps {
                dir("${env.CLONE_PATH}/terraform") {
                    sh 'terraform apply -auto-approve'
                }
            }
        }

        stage('Get ECR Repo URL') {
            steps {
                dir("${env.CLONE_PATH}/terraform") {
                    script {
                        env.ECR_REPOSITORY_URL = sh(script: 'terraform output -raw ecr_repository_url', returnStdout: true).trim()
                    }
                }
                echo "ECR Repository URL: ${env.ECR_REPOSITORY_URL}"
            }
        }

        stage('Docker Build and Push') {
            steps {
                script {
                    def imageName = "${env.ECR_REPOSITORY_URL}:latest"
                    echo "Image Name: ${imageName}"
                    dir("${env.CLONE_PATH}") {
                        sh "docker build -t ${imageName} ."
                        sh "aws ecr get-login-password --region ${env.AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${env.ECR_REPOSITORY_URL.tokenize('/')[0]}"
                        sh "docker push ${imageName}"
                    }
                }
            }
        }

        stage('Update ECS Task Definition') {
            steps {
                dir("${env.CLONE_PATH}/terraform") {
                    sh 'terraform apply -auto-approve'
                }
            }
        }
    }
}
</deploraFile>
```

```
<deploraFile type="README" filePath="README.md">
# React Application Deployment to AWS with Docker, Terraform, and Jenkins

## Overview

This project outlines the steps to deploy a React application to AWS using Docker for containerization, Terraform for Infrastructure as Code (IaC), and Jenkins for Continuous Integration and Continuous Deployment (CI/CD).

## Prerequisites

*   AWS Account
*   Terraform installed
*   Jenkins installed with AWS credentials configured
*   Docker installed

## Configuration

### Terraform Variables

Customize the deployment by modifying the `terraform.tfvars` file.  Here are some key variables:

*   `aws_region`: The AWS region to deploy to (default: `us-east-1`).
*   `cluster_name`: The name of the ECS cluster (default: `react-app-cluster`).
*   `ecr_repository_name`: The name of the ECR repository (default: `react-app-repo`).
*   `subnet_ids`:  A list of subnet IDs where the ECS tasks will run.
*   `security_group_ids`: A list of security group IDs to associate with the ECS tasks.

### Jenkins Configuration

1.  Ensure the AWS credentials are set up in Jenkins under Manage Jenkins -> Credentials.
2.  Configure the Jenkinsfile in your pipeline.

## Deployment Steps

1.  **Terraform Initialization:**
    *   Navigate to the `terraform` directory: `cd terraform`
    *   Initialize Terraform: `terraform init`
2.  **Terraform Apply:**
    *   Apply the Terraform configuration: `terraform apply -var-file="terraform.tfvars"`
3.  **Build and Push Docker Image**
    *   Run the jenkins pipeline to build and push the Docker image to ECR.
4.  **Update ECS Task Definition:**
    *   Run the jenkins pipeline to update the task definition.
</deploraFile>
'''

    file_parser = FileParser()
    files, files_content = file_parser.parse(txtx)
    print([f["file_name"] for f in files])