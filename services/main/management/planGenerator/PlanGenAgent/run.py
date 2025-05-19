# Standard library imports
import asyncio
import json

# Typing imports
from typing import Literal, Dict, List

# Third-party library imports
from pydantic import BaseModel, Field
from langchain_core.messages import ToolMessage, convert_to_messages
from langchain_core.tools import tool
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END, MessagesState

# Local application imports
from core.logger import logger
from services.main.utils.prompts.service import PromptManagerService
from services.main.management.planGenerator.FileParser import FileParser
from services.main.management.planGenerator.TerraformDocScraper import TerraformDocScraper
from services.main.management.planGenerator.PlanGenAgent.agentPrompts import (
    identify_resources_prompt,
    docker_prompt,
)




rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.2, 
    check_every_n_seconds=0.1,
    max_bucket_size=10,
)

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    rate_limiter=rate_limiter,
)
# gen_model = ChatOpenAI(model="gpt-4o")
# model = ChatGroq(
#     model="llama-3.3-70b-specdec",
#     temperature=0.5,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
# )
gen_model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

class DeploymentRecommendation(BaseModel):
    deployment_recommendation: str = Field(description="The recommended deployment option.")
    reason: str = Field(description="The reason for the recommendation.")

class DeploymentRecommendationAgent:
    def __init__(self):
        self.model = model
        self.system_prompt = """You are an expert deployment solution architect. Your task is to classify the best deployment plan for the given project based on its details, user preferences, and specific prompt.
                                ### Deployment Options:
                                1. **Dockerized Deployments (Containerization)**:
                                - Suitable for small to medium projects.
                                - Benefits include portability, consistency across environments, and simplicity.
                                2. **Kubernetes-Orchestrated Deployment**:
                                - Best for large-scale projects requiring scalability, microservices orchestration, or advanced features like load balancing and rolling updates.
                                3. **AMI/VM Image-Based Deployment**:
                                - Ideal for immutable infrastructure, compliance with strict security or performance requirements, or traditional VM-based setups.
                                """
    
    def invoke(self, state) -> Command[Literal["supervisor"]]:
        print("Invoking recommendation agent")
        data = agentState.format_context()
        prompt = f"{self.system_prompt}\n\n{data}"
        response = self.model.with_structured_output(DeploymentRecommendation).invoke(prompt)
        agentState.deployment_strategy = response

        print("Deployment recommendation")
        print(response.deployment_recommendation)
        return Command(goto="supervisor", update={"messages": [response.deployment_recommendation]})

class ResourceCollectorAgent:
    def __init__(self):
        self.model = model
        self.run_count = 0
        self.max_runs = 3
        
    def invoke(self, state) -> Command[Literal["tf_doc_agent", "jenkins_doc_agent"]]:
        if self.run_count >= self.max_runs:
            return Command(goto="supervisor", update={"messages": ["Resource collection completed."]})
        self.run_count += 1
        
        print("Invoking resource agent")
        system_prompt = f"""You are an expert deployment solution architect. Your task is to identify the resources required for the deployment based on the project details and user preferences. Terraform files and the jenkin pipeline need to be created later. Identify the data sources needed.
                                You have the following tools. {', '.join(f"{agent}: {agent_descriptions[agent]}" for agent in agents_for_resource.keys())}.
                                You already know about {", ".join([doc["name"] for doc in agentState.resource_documents.get("terraform", []) if "name" in doc])}. 
                                Only return the next agent to invoke or 'supervisor' to continue the next steps if you have identified enough resources."""
    
        data = agentState.format_context()
        prompt = f"{system_prompt}\n\n{data}"
        response = self.model.invoke(prompt)
        
        next_agent = parse_next_agent(response.content)
        print(f"Next agent is {next_agent}")
        if next_agent:
            return Command(goto=next_agent, update={"messages": [response]})
        else:
            return Command(goto=END, update={"messages": [response]})
    
class JenkinsDocumenationAgent:
    def __init__(self):
        self.model = model
    
    def invoke(self, state) -> Command[Literal["resource_agent"]]:
        response = self.model.invoke("hi")

        return Command(goto="resource_agent", update={"messages": [response]})


class TerraformDocumentationAgent:
    def __init__(self):
        self.model = model
        self.prompt_manager = PromptManagerService()
        self.file_parser = FileParser()
    
    def invoke(self, state) -> Command[Literal["resource_agent"]]:
        print("Invoking Terraform documentation agent")
        deployment_recommendation = agentState.deployment_strategy.deployment_recommendation if agentState.deployment_strategy else "Dockerized Deployments (Containerization)"
    

        prompt = identify_resources_prompt.format(deployment_recommendation, 
                                                  agentState.format_context(), 
                                                  ", ".join([doc["name"] for doc in agentState.resource_documents.get("terraform", []) if "name" in doc])
)

        ai_msg = model.bind_tools([fetch_resource_definitions]).invoke(prompt)
        print("Response from Terraform documentation agent", ai_msg.tool_calls)

        if ai_msg.tool_calls:
            tool_responses = []
            for call in ai_msg.tool_calls:
                tool_name = call["name"]
                tool_call_id = call["id"]
                arguments = call["args"]

                if tool_name == "fetch_resource_definitions":
                    resource_defs = [ResourceDefinition(**res) for res in arguments["resources"]]
                    print("Resource definitions", resource_defs)
                    result = fetch_resource_definitions.invoke({"resources": [res.model_dump() for res in resource_defs]})
                    print("Result from fetch_resource_definitions", result[:20])
                    for doc in result:
                        if "terraform" not in agentState.resource_documents:
                            agentState.resource_documents["terraform"] = []
                        agentState.resource_documents["terraform"].append(doc)

                    # Append actual results
                    tool_msg = ToolMessage(content=json.dumps(result), tool_call_id=tool_call_id)
                    tool_responses.append(tool_msg)

        # Return with real execution results
        print("TOOL EXECUTION RESULTS")
        return Command(
            goto="resource_agent",
            update={"messages": [ai_msg]}
        )

class DeploymentPlanGeneratorAgent:
    def __init__(self):
        self.model = gen_model
    
    def invoke(self, state) -> Command[Literal[END]]:
        prompt = docker_prompt.format(agentState.format_context(), agentState.format_resources())
        print(prompt)
        response = self.model.invoke(prompt)
        agentState.deployment_solution = response.content

        return Command(goto=END, update={"messages": [response]})


class Supervisor:
    def __init__(self):
        self.model = model
    
    def invoke(self, super_state) -> Command[Literal["recommendation_agent", "resource_agent", "plan_agent", END]]:
        print("Invoking supervisor")
        response = self.model.invoke(f"""You are an expert deployment solution architect. Your task is to generate a deployment plan using the agents you have access to. 
            You have the following tools: {', '.join(f"{agent}: {agent_descriptions[agent]}" for agent in agents_for_supervisor.keys())}. 
            You already know {agentState.format_state()}. 
            It is adviced to get the recommendation, then resources, then generate a plan but you can choose any order that optimizes the workflow.
            Only return the next agent to invoke.
            """)

            
        next_agent = parse_next_agent(response.content)
        print(f"Next agent is {next_agent}")
        if next_agent:
            return Command(goto=next_agent, update={"messages": [response]})
        else:
            return Command(goto=END, update={"messages": [response]})




class TerraformDocumentationTool:
    def __init__(self, scraper: TerraformDocScraper):
        self.scraper = scraper
        # asyncio.run(self.scraper.initialize_browser())
    
    def fetch_resources(self, resources: List[Dict[str, str]]):
        resource_docs = []
        for resource in resources:
            name = resource.get("name")
            try:
                definition = asyncio.wait_for(self.scraper.fetch_definition(name), timeout=10)
                if definition:
                    resource_docs.append({"name": name, "content": definition})
            except asyncio.TimeoutError:
                definition = "Timeout occurred while fetching the definition."
            
        
        return resource_docs

terraform_doc_scraper = TerraformDocumentationTool(TerraformDocScraper())



class ResourceDefinition(BaseModel):
    name: str
    description: str  # Optional, but helps structure the request.

@tool
async def fetch_resource_definitions(resources: List[ResourceDefinition]) -> List[Dict[str, str]]:
    """
    Fetch Terraform resource definitions based on a list of resources.

    Args:
        resources (List[ResourceDefinition]): List of resources to fetch documentation for.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing resource definitions.
    """
    res = await terraform_doc_scraper.fetch_resources([{"name": res.name} for res in resources])
    return res



agent_descriptions = {
    "recommendation_agent": "This agent is responsible for generating a deployment recommendation based on the project details and user preferences.",
    "resource_agent": "This agent is responsible for collecting the resources required for the deployment.",
    "plan_agent": "This agent is responsible for generating a deployment plan.",
    "tf_doc_agent": "This agent is responsible for scraping Terraform documentation for the identified resources.",
    "jenkins_doc_agent": "This agent is responsible for scraping Jenkins documentations required.",
    "supervisor": "This agent is responsible for managing the other agents.",
}

agents_for_supervisor = {
    "recommendation_agent": "recommendation_agent",
    "resource_agent": "resource_agent",
    "plan_agent": "plan_agent",
}

agents_for_resource = {
    "tf_doc_agent": "tf_doc_agent",
    "jenkins_doc_agent": "jenkins_doc_agent",
}

class Context:
    def __init__(self, 
                 project_data: Dict[str, str] = None, 
                 user_preferences: Dict[str, str] = None, 
                 user_prompt: str = "", 
                 chat_history: List[str] = None):
        
        self.project_data: Dict[str, str] = project_data if project_data is not None else {}
        self.user_preferences: Dict[str, str] = user_preferences if user_preferences is not None else {}
        self.user_prompt: str = user_prompt
        self.chat_history: List[str] = chat_history if chat_history is not None else []


class AgentState:
    def __init__(self, context: Context = None):
        self.context = context

        self.messages: List[str] = []
        self.deployment_strategy: str = ""
        self.identified_resources: List[Dict[str, str]] = []
        self.resource_documents: Dict[str, List[Dict[str, str]]] = {}
        self.deployment_solution: str = ""
        self.validated_files: List[Dict] = []
    
    def format_state(self):
        return {
            key: value for key, value in {
                "messages": self.messages,
                "context": self.context.__dict__,
                "deployment_strategy": self.deployment_strategy,
                "identified_resources": self.identified_resources,
                "resource_documents": self.resource_documents,
                "deployment_solution": self.deployment_solution,
                "validated_files": self.validated_files,
            }.items() if value
        }
    
    def format_context(self):
        return {
            key: value for key, value in {
                "project_data": self.context.project_data,
                "user_preferences": self.context.user_preferences,
                "user_prompt": self.context.user_prompt,
                "chat_history": self.context.chat_history,
            }.items() if value
        }

    def format_resources(self):
        formatted_resources = []
        
        for tool, documents in self.resource_documents.items():
            tool_resources = [f"{doc['name']}: {doc.get('content', 'No content available')}" for doc in documents]
            formatted_resources.append(f"{tool}:\n" + "\n".join(tool_resources))
        
        return "\n\n".join(formatted_resources)





builder = StateGraph(MessagesState)
builder.add_node("supervisor", Supervisor().invoke)

builder.add_node("recommendation_agent", DeploymentRecommendationAgent().invoke)
builder.add_node("plan_agent", DeploymentPlanGeneratorAgent().invoke)

builder.add_node("resource_agent", ResourceCollectorAgent().invoke)
builder.add_node("tf_doc_agent", TerraformDocumentationAgent().invoke)
builder.add_node("jenkins_doc_agent", JenkinsDocumenationAgent().invoke)


builder.add_edge(START, "supervisor")

supervisor = builder.compile()



context = Context()
agentState = AgentState(context)

def parse_next_agent(text):

    for agent in agent_descriptions:
        if f"{agent}" in text:
            return f"{agent}"




def pretty_print_messages(update):
    if isinstance(update, tuple):
        ns, update = update
        # skip parent graph updates in the printouts
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"\nUpdate from subgraph {graph_id}:")

    for node_name, node_update in update.items():
        print(f"\nUpdate from node {node_name}:")

        for m in convert_to_messages(node_update["messages"]):
            m.pretty_print()
        print("\n")


async def runME():
    for chunk in supervisor.stream(
        {"messages": [("user", "")]}
    ):
        pretty_print_messages(chunk)

def saveGraph():
    try:
        img_data = supervisor.get_graph().draw_mermaid_png()
        with open("graph_output.png", "wb") as f:
            f.write(img_data)
        print("Workflow diagram saved to graph_output.png")
    except Exception as e:
        print(f"Error generating diagram: {e}")


def invokeAgent(preferences, project_data, user_prompt, chat_history):
    context = Context(project_data, preferences, user_prompt, chat_history)
    agentState.context = context
    for chunk in supervisor.stream(
        {"messages": [("user", "")]}
    ):
        pretty_print_messages(chunk)
    
    return agentState

if __name__ == "__main__":
    saveGraph()
    # asyncio.run(runME())
    invokeAgent(preferences, project_data, user_prompt, chat_history)
        