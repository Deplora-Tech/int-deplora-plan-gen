import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import UserCreate, UserOut, UserQuery
from models.user import User
from db.database import get_db
from config import logger

router = APIRouter()
def save(db, instance):
    db.add(instance)
    db.commit()
    db.refresh(instance)



# api method to reequest from openAi api to get a response for a deplyment plan for a given techstack and template which conteins all required data
@router.post("/get-deployment-plan")
def get_deployment_plan():
    logger.info("get_deployment_plan")
    return {"message": "get_deployment_plan"}

