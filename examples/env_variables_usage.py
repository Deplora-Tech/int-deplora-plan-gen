"""
Example of how to use project-specific environment variables in your application.
This demonstrates storing, retrieving, and using encrypted environment variables
that are associated with specific projects.
"""

import sys
import os
import asyncio

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import env_manager


async def store_project_credentials(project_id: str):
    """Example function to store project-specific credentials"""

    # Store AWS credentials for a specific project
    await env_manager.set_env_variable(
        project_id, "AWS_ACCESS_KEY_ID", "AKIA1234567890EXAMPLE"
    )
    await env_manager.set_env_variable(
        project_id, "AWS_SECRET_ACCESS_KEY", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    )
    await env_manager.set_env_variable(project_id, "AWS_REGION", "us-west-2")

    # Store database credentials
    await env_manager.set_env_variable(project_id, "DB_HOST", "database.example.com")
    await env_manager.set_env_variable(project_id, "DB_USER", "project_user")
    await env_manager.set_env_variable(project_id, "DB_PASSWORD", "secure_password_123")

    print(f"✅ Stored credentials for project {project_id}")


async def use_project_credentials(project_id: str):
    """Example function demonstrating how to use project-specific credentials"""

    # Retrieve all environment variables for the project
    env_vars = await env_manager.get_all_env_variables(project_id)

    print(
        f"🔐 Retrieved {len(env_vars)} environment variables for project {project_id}"
    )

    # Example: Using AWS credentials from the stored environment variables
    print("\nConfiguring AWS client with project-specific credentials:")
    print(
        f"  AWS_ACCESS_KEY_ID: {env_vars.get('AWS_ACCESS_KEY_ID', '[not set]')[:5]}..."
    )
    print(
        f"  AWS_SECRET_ACCESS_KEY: {env_vars.get('AWS_SECRET_ACCESS_KEY', '[not set]')[:5]}..."
    )
    print(f"  AWS_REGION: {env_vars.get('AWS_REGION', '[not set]')}")

    # Example: Using database credentials
    print("\nConfiguring database connection with project-specific credentials:")
    db_host = env_vars.get("DB_HOST", "[not set]")
    db_user = env_vars.get("DB_USER", "[not set]")
    db_password = env_vars.get("DB_PASSWORD", "[not set]")

    if all([db_host, db_user, db_password]):
        connection_string = f"postgresql://{db_user}:****@{db_host}/database"
        print(f"  Connection string: {connection_string}")
    else:
        print("  Missing database credentials")


async def main():
    # Example project ID (in a real application, this would come from your project database)
    project_id = "project-123456"

    # Store project-specific environment variables
    await store_project_credentials(project_id)

    # Use the stored environment variables
    await use_project_credentials(project_id)

    # Clean up (for demo purposes only)
    deleted_count = await env_manager.delete_all_project_env_variables(project_id)
    print(f"\n🧹 Cleaned up {deleted_count} environment variables")


if __name__ == "__main__":
    asyncio.run(main())
