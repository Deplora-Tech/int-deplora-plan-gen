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
    Now, you are an intent classifier for a chatbot that handles deployment-related queries. The input categories are defined below:
    
    Intent Categories:
    1. **unrelated_question**: Queries that are not related to deployment plans or other deployment-related topics.
    2. **modify_deployment_plan**: Queries where the user is asking to modify or update an existing deployment plan.
    3. **ask_plan_details**: Queries where the user is asking for details or information about a deployment plan.
    4. **related_question**: Queries that are related to deployment but do not directly ask to create or modify a deployment plan.
    5. **create_deployment_plan**: Queries where the user is requesting to create a new deployment plan.
    6. **greeting**: User greetings, such as "hello", "hi", etc.
    7. **insult**: Insulting or offensive remarks.

    Input: 
    {combined_query}

    Output:
    <one of the intents from the list: 'unrelated_question', 'modify_deployment_plan', 'ask_plan_details', 'related_question', 'create_deployment_plan', 'greeting', 'insult'>
"""


    try:
        intent = await llm_service.llm_request(prompt)
        intent = intent.strip().lower()
        # print(f"Intent classification response: {ans}")
        # intent = ans.split(":")[1].strip()
        logger.debug(f"Intent classification response: {intent}")
        return intent
    except requests.exceptions.RequestException as e:
        logger.error(f"Error classifying intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

