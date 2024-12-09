# app/services/management/api.py
from fastapi import APIRouter
from .service import ManagementService

router = APIRouter()
service = ManagementService()

@router.post("/generate-deployment")
async def generate_deployment_plan(request: dict):
    return await service.generate_deployment_plan(request)
