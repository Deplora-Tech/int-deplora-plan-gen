async def add_user_node(self, id, organization):
    """
    Add a new user to the Neo4j database if they don't already exist and return the node ID.
    """

    records, summery, keys = await self.driver.execute_query(
        """
        MERGE (u:User {name: $id, type: 'User'})
        ON CREATE SET u.organization = $organization
        RETURN elementId(u) AS uid
        """,
        id=id,
        organization=organization,
        database_=self.database,
    )

    id = records[0]["uid"]

    return id


async def add_entity_node(self, entity):
    """
    Add a new entity to the Neo4j database if it doesn't already exist and return the node ID.
    """
    
    entity_embedding = self.embeding_manager.calculate_embedding(entity)
    
    # Check for similar entities
    query = """
    MATCH (e:Entity)
    WHERE e.embedding IS NOT NULL
    WITH e, gds.similarity.cosine(e.embedding, $embedding) AS similarity
    WHERE similarity > 0.8
    RETURN e.name AS similarName, similarity
    ORDER BY similarity DESC
    LIMIT 1
    """
    
    similar_records, summery, keys = await self.driver.execute_query(query, embedding=entity_embedding)


    # If similar nodes are found, return their names
    if similar_records:
        return {
            "status": "similar_found",
            "similar_node": similar_records[0]["similarName"],
            "similarity_score": similar_records[0]["similarity"],
        }

    
    add_node_query = """
        MERGE (e:Entity {name: $entity})
        ON CREATE SET e.embedding = $embedding
        RETURN elementId(e) AS eid
        """
        
    new_records, _, _ = await self.driver.execute_query(
        add_node_query,
        entity=entity,
        embedding=entity_embedding,
        database_=self.database,
    )

    eid = new_records[0]["eid"]

    return {
        "status": "new_node_added",
            "node_id": eid,
        }