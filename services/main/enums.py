from enum import Enum, auto

class PlanValidationType(Enum):
    TERRAFORM = auto()
    JENKINS = auto()


class DeploymentOptions(Enum):
    DOCKERIZED_DEPLOYMENT = "Dockerized Deployments (Containerization)"
    KUBERNETES_DEPLOYMENT = "Kubernetes-Orchestrated Deployment"
    VM_DEPLOYMENT = "MI/VM Image-Based Deployment"
    
    