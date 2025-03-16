from typing import Literal, Dict, List
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END, MessagesState

import json
import asyncio
import concurrent.futures
import traceback

from services.main.workers.llm_worker import LLMService
from services.main.utils.prompts.service import PromptManagerService
from services.main.enums import DeploymentOptions
from services.main.management.planGenerator.FileParser import FileParser

from services.main.management.planGenerator.TerraformDocScraper import (
    TerraformDocScraper,
)
from services.main.management.validationManager.service import ValidatorService
from core.logger import logger



model = ChatOpenAI(model="gpt-4o")




