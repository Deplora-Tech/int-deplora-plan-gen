import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")

def invoke_groq(prompt):
    """
    Invokes the ChatGroq model with a given prompt.
    """
    response = llm.invoke(prompt)
    return response
