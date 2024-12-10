from utils.utils import replace_special_characters

async def add_entity_user_edge(self, user, entity, relationship, isPositive=True):
    """
    Add an edge between a user and an entity in the Neo4j database.
    Check if a similar relationship (based on cosine similarity) already exists and update its weight if found.
    """
    # Define the multiplier for weight calculation
    multiplier = 0.1

    # Replace special characters in the relationship name
    relationship = replace_special_characters(relationship)

    # Calculate embedding for the relationship
    relationship_embedding = self.embeding_manager.calculate_embedding(relationship)

    # Query 1: Check for existing relationships with similarity > 0.8
    similarity_query = """
    MATCH (u:User {name: $userName})-[r]->(e:Entity {name: $entityName})
    WHERE type(r) = $relationship
    AND r.embedding IS NOT NULL
    WITH r, gds.similarity.cosine(r.embedding, $relationship_embedding) AS similarity
    WHERE similarity > 0.8
    RETURN r.weight AS currentWeight, elementId(r) AS edgeId, type(r) AS relationship
    LIMIT 1
    """
    similar_records, _, _ = await self.driver.execute_query(
        similarity_query,
        userName=user,
        entityName=entity,
        relationship=relationship,
        relationship_embedding=relationship_embedding,
        database_=self.database,
    )

    # Check if a similar relationship already exists
    if similar_records:
        current_weight = similar_records[0]["currentWeight"]
        edge_id = similar_records[0]["edgeId"]

        # Adjust the weight for the existing relationship
        if isPositive:
            new_weight = current_weight + (1 - current_weight) * multiplier
        else:
            new_weight = current_weight - current_weight * multiplier
            
        
        print(f"Updating edge between {user} and {entity} with relationship {similar_records[0]["relationship"]} (matched for {relationship}) of current weight {current_weight} to new weight {new_weight}")
        # Update the weight of the existing relationship
        update_query = """
        MATCH ()-[r]->()
        WHERE elementId(r) = $edgeId
        SET r.weight = $new_weight
        RETURN r
        """
        await self.driver.execute_query(
            update_query,
            edgeId=edge_id,
            new_weight=new_weight,
            database_=self.database,
        )

        return {
            "status": "edge_updated",
            "edge_id": edge_id,
            "new_weight": new_weight,
        }

    # Query 2: Add a new relationship with an initial weight
    initial_weight = 0.5
    if isPositive:
        initial_weight += multiplier
    else:
        initial_weight -= multiplier

    add_edge_query = f"""
    MATCH (u:User {{name: $user}})
    MATCH (e:Entity {{name: $entity}})
    MERGE (u)-[r:{relationship}]->(e)
    SET r.weight = $initial_weight,
        r.embedding = $relationship_embedding
    RETURN elementId(r) AS edgeId
    """
    new_edge_records, _, _ = await self.driver.execute_query(
        add_edge_query,
        user=user,
        entity=entity,
        relationship_embedding=relationship_embedding,
        initial_weight=initial_weight,
        database_=self.database,
    )

    new_edge_id = new_edge_records[0]["edgeId"]

    return {
        "status": "new_edge_added",
        "edge_id": new_edge_id,
        "initial_weight": initial_weight,
    }
