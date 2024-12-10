import os
import json

from .embedings.embedingManager import EmbeddingManager
from .graph.manage import setup
from .graph.nodes import add_user_node, add_entity_node
from .graph.edges import add_entity_user_edge
from .update.extract_entities import extract_entities_and_relationships, clean_extracted_entities

class ContextGraph:
    def __init__(self):
        """
        Initialize the class variables.
        """
        self.database = "neo4j"
        self.driver = None
        self.embeding_manager = EmbeddingManager("all-MiniLM-L6-v2")
        
    async def setup(self, uri):
        """
        Asynchronously setup the Neo4j driver.
        """
        self.driver = await setup(uri)
    
    async def add_user(self, name, organization):
        """
        Add a new user to the neo4j database.
        """
        return await add_user_node(self, name, organization)
        

    async def update(self, user, prompt):
        entities = await extract_entities_and_relationships(prompt)
        cleaned_entities = await clean_extracted_entities(entities, prompt)
        
        for entity in cleaned_entities.get("Entities", []):
            res =  await add_entity_node(self, entity)
            isPositive = cleaned_entities["Entities"][entity]["relationship"] == "positive"
            
            if res.get("status") == "similar_found":
                print(f"Similar node found for {entity}: {res['similar_node']} with similarity score {res['similarity_score']}")
                
                await add_entity_user_edge(self, user, res['similar_node'], cleaned_entities["Entities"][entity]["type"], isPositive)
                
            else:   
                await add_entity_user_edge(self, user, entity, cleaned_entities["Entities"][entity]["type"], isPositive)
        
        
    
    
    def pprint(self, js):
        print(json.dumps(js, indent=4))
