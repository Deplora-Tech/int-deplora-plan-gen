import json
from core.llm_interface.chat_groq import invoke_groq

async def extract_entities_and_relationships(prompt):
    """
    Extracts and cleans relevant entities, relationships, and constraints dynamically.
    Filters out meaningless entities such as generic terms or unqualified metrics.
    """
    system_prompt = """
    You are an intelligent prompt classification and entity extraction engine. Your job is to analyze the user’s input, identify the **type of prompt**, extract relevant **entities**, determine **relationships** between them, and filter out meaningless or generic entities and relationships.

    ### Instructions:
    1. **Classify the prompt** into one of the following types:
      - **Deployment Request / Action**: A request to deploy or take an action.
      - **Error / Issue Reporting**: Reporting a failure, issue, or error.
      - **Suggestion / Recommendation**: Asking for advice, suggestions, or alternatives.
      - **Success / Confirmation**: Confirming a successful operation.
      - **Query / Information Request**: Requesting information or clarification.
      - **Configuration Change / Update**: Requesting a change or update in configuration.

    2. **Extract Entities and Relationships:**
      - Identify all **relevant entities** mentioned (e.g., cloud providers, services, regions).
      - **Exclude generic terms** like "code," "data," "performance," or "information" unless explicitly tied to a meaningful type or specific context (e.g., "API latency performance").
      - Determine the **relationship** between these entities (e.g., "Deploy to", "Avoid using").
      - Label each **relationship** as either **positive** or **negative**.

    3. **Filter Meaningless Entities and Relationships:**
      - Remove entities that are overly generic, ambiguous, or unqualified (e.g., "performance" or "code").
      - Retain only entities that provide actionable insights, specific details, or meaningful contributions to the context.

    4. **Detect Constraints:**
      - Identify any positive or negative **constraints** mentioned (e.g., "Enable autoscaling", "Do not use Kubernetes").

    5. **Format your response** as structured JSON:

    {
      "PromptType": "<DeploymentRequest | Error | Suggestion | Success>",
      "Entities": {
        "entity1": {
          "type": "<EntityType>",
          "relationship": "<positive | negative>"
        },
        "entity2": {
          "type": "<EntityType>",
          "relationship": "<positive | negative>"
        }
      }
    }

    ### Example:
    User Prompt: "Deploy a React app to AWs. Ensure it is GDPR compliant. Avoid Kubernetes. Use a PostgreSQL database. Notify the team via Slack. Monitor API latency performance with New Relic. Do not use Docker."

    Response:
    {
      "PromptType": "DeploymentRequest",
      "Entities": {
          "React app": {
              "type": "Application",
              "relationship": "positive"
          },
          "AWs": {
              "type": "CloudProvider",
              "relationship": "positive"
          },
          "GDPR": {
              "type": "PrivacyCompliance",
              "relationship": "positive"
          },
          "Kubernetes": {
              "type": "ContainerPlatform",
              "relationship": "negative"
          },
          "PostgreSQL": {
              "type": "DatabaseManagementSystem",
              "relationship": "positive"
          },
          "Slack": {
              "type": "CommunicationTool",
              "relationship": "positive"
          },
          "New Relic": {
              "type": "PerformanceMonitoringTool",
              "relationship": "positive"
          },
          "Docker": {
              "type": "ContainerPlatform",
              "relationship": "negative"
          }
      }
    }
    """
    
    # Combine the system prompt with the user prompt
    combined_prompt = f"{system_prompt}\nUser Prompt: {prompt}\nExtract and format the relevant information as structured JSON. ONLY INCLUDE THE JSON. NO ADDITIONAL TEXT."
    response = invoke_groq(combined_prompt)

    try:
        extracted_data = json.loads(response.content)
        return extracted_data
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response.")
        return None



async def clean_extracted_entities(data, prompt_context):
    """
    Dynamically cleans extracted entities by leveraging an LLM to filter out meaningless or generic terms.

    Parameters:
        data (dict): The JSON-like data structure containing entities and relationships.
        prompt_context (str): The context or original user prompt to help the LLM understand the situation.

    Returns:
        dict: A cleaned data structure with only meaningful entities and relationships.
    """
    if not data or "Entities" not in data:
        return data  # Return as is if the structure is not as expected

    entities = data.get("Entities", {})
    if not entities:
        return data  # No entities to process

    # Construct a dynamic LLM prompt to evaluate the entities
    cleaning_prompt = f"""
    You are an expert entity evaluator for a natural language processing system. Your task is to clean up extracted entities and relationships.

    ### Context:
    The user provided this prompt: "{prompt_context}"

    ### Entities to Evaluate:
    {json.dumps(entities, indent=4)}

    ### Instructions:
    1. Identify entities that are too vague, generic, or irrelevant to the context of the user prompt.
    2. Mark each entity as either "meaningful" or "meaningless."
    3. If an entity is vague or irrelevant (e.g., "code," "data," "performance"), classify it as "meaningless."
    4. Provide your response as JSON with the following structure:
    {{
        "Entity1": "meaningful",
        "Entity2": "meaningless",
        ...
    }}
    ONLY INCLUDE THE JSON. NO ADDITIONAL TEXT.
    """

    # Invoke the LLM with the cleaning prompt
    response = invoke_groq(cleaning_prompt)

    try:
        evaluation_result = json.loads(response.content)
        
        # Filter out entities based on LLM's evaluation
        cleaned_entities = {
            key: value for key, value in entities.items()
            if evaluation_result.get(key, "meaningless") == "meaningful"
        }

        # Replace the original entities with the cleaned ones
        data["Entities"] = cleaned_entities
        return data
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response from LLM.")
        return data
