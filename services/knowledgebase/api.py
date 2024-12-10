from core.contextGaph import ContextGraph

# Singleton instance of ContextGraph
context_graph = ContextGraph()

async def setup_context_graph(uri: str):
    """
    Initialize the ContextGraph connection.
    
    Args:
        uri (str): The URI for the Neo4j database.
    """
    await context_graph.setup(uri)

async def add_user(username: str, organization: str):
    """
    Add a user to the ContextGraph.
    
    Args:
        username (str): The username to add.
        organization (str): The organization associated with the user.
    
    Returns:
        str: Success message or error message.
    """
    try:
        await context_graph.add_user(username, organization)
        return "User added successfully"
    except Exception as e:
        return f"Error adding user: {str(e)}"

async def update_context(username: str, prompt: str):
    """
    Update the context for a user in the ContextGraph.
    
    Args:
        username (str): The username to update.
        prompt (str): The context or prompt to associate with the user.
    
    Returns:
        dict: Result of the update or an error message.
    """
    try:
        result = await context_graph.update(username, prompt)
        return {"message": "Context updated successfully", "result": result}
    except Exception as e:
        return {"error": f"Error updating context: {str(e)}"}

async def close_context_graph():
    """
    Close the ContextGraph connection.
    """
    await context_graph.close()
