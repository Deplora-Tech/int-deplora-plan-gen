import asyncio
from fastapi import APIRouter, HTTPException
from services.main.excecutor.service import excecute_pipeline, abort_pipeline, get_status, check_env_variables
from services.main.excecutor.models import ExcecutionRequest
from services.main.management.api import  handle_file_change
from services.main.communication.models import FileChangeRequest
from fastapi import Request

router = APIRouter()

@router.get("/check-env/{session_id}")
async def check_env(session_id: str):
    """
    Endpoint to check environment variables for a given session.
    """
    try:
        user_vars, common_vars = await check_env_variables(session_id)

        if not user_vars and not common_vars:
            raise HTTPException(status_code=400, detail="No environment variables found")
        
        return { "user_vars": user_vars, "common_vars": common_vars, "status": "Environment variables checked successfully" }
    

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
async def execute(request: ExcecutionRequest):

    env_variables = request.env_variables
    session_id = request.session_id
    print(f"Received env_variables: {env_variables}")
    tfvars = generate_tfvars(env_variables)
    await handle_file_change(FileChangeRequest(
        session_id=session_id,
        file_path="terraform/terraform.tfvars",
        file_content=tfvars
    ))

    build_id = await excecute_pipeline(session_id)

    return {"status": "Pipeline execution started", "session_id": session_id, "build_id": build_id}

@router.post("/abort/{session_id}/{build_id}")
async def abort(session_id: str, build_id: str):

    await abort_pipeline(session_id, build_id)
    return {"status": "Pipeline aborted", "session_id": session_id, "build_id": build_id}

@router.post("/status/{session_id}/{build_id}")
async def status(session_id: str, build_id: str):
    build_info = await get_status(session_id, build_id)
    if build_info is None:
        raise HTTPException(status_code=404, detail="Build not found")
    return build_info



def generate_tfvars(variable_dict: dict) -> str:
    """
    Generate Terraform .tfvars file content from a variable dictionary.
    
    Args:
        variable_dict (dict): Dictionary with variable names as keys and their metadata as values.
        
    Returns:
        str: Formatted string content for a .tfvars file.
    """
    lines = []

    for var_name, attrs in variable_dict.items():
        if "default" not in attrs:
            continue  # skip variables without default values

        value = attrs["default"]
        var_type = attrs.get("type", "")

        # Handle lists from comma-separated string
        if var_type.startswith("list") and isinstance(value, str):
            items = [item.strip() for item in value.split(",")]
            formatted_value = "[" + ", ".join(f'"{item}"' for item in items) + "]"

        # Handle numeric types
        elif var_type == "number":
            formatted_value = str(value)

        # Handle boolean
        elif isinstance(value, bool):
            formatted_value = "true" if value else "false"

        # Default to quoted string
        else:
            formatted_value = f'"{value}"'

        lines.append(f'{var_name} = {formatted_value}')

    return "\n".join(lines)
