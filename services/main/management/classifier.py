import requests
from fastapi import HTTPException
from core.logger import logger
from services.main.workers.llm_worker import LLMService

llm_service = LLMService()

async def classify_intent(user_query, chat_history=None):

    # Combine chat history with user query if context is available
    if chat_history:
        combined_query = f"Chat History: {chat_history}\nUser Query: {user_query}"
    else:
        combined_query = user_query

    prompt = f"""
    Now You are an intent classifier for a chatbot that handles deployment-related queries. the related inputs are given,
    Classify the intent of the given input into one of the following categories:
    1. Deployment Request: When the user is requesting or asking to create a deployment plan for the project.
    2. Other: For unrelated or ambiguous queries.

    Input: 
    {combined_query}

    Output must be in below format:
    Intent: <one of 'Deployment Request' or 'Other'>
    """

    try:
        ans = await llm_service.llm_request(prompt)
        intent = ans.split(":")[1].strip()
        logger.debug(f"Intent classification response: {intent}")
        return intent
    except requests.exceptions.RequestException as e:
        logger.error(f"Error classifying intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

