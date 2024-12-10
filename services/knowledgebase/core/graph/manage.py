import os

from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv

async def setup():
        """
        Asynchronous setup for the Neo4j driver.
        """
        # Load environment variables
        load_dotenv(override=True)
        driver = AsyncGraphDatabase.driver(
            os.getenv("NEO4J_URI",
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )
        
        try:
            # Verify connectivity to the database
            await driver.verify_connectivity()
            print("Connection successful!")
            return driver
        except Exception as e:
            print(f"Failed to connect: {e}")
            return None
