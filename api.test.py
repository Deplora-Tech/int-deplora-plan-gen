import re
import ast

def parse_terraform_blocks(file_content: str) -> dict:
    """
    Parse Terraform variables declared as blocks:
    variable "name" {
      default = value
    }
    Returns dict of {variable_name: default_value or None}.
    """
    variables = {}
    var_blocks = re.findall(r'variable\s+"([^"]+)"\s*{([^}]+)}', file_content, re.DOTALL)
    for var_name, block_body in var_blocks:
        match = re.search(r'default\s*=\s*(.+)', block_body)
        if match:
            raw_value = match.group(1).strip()
            raw_value = raw_value.split('\n')[0].split('#')[0].strip()  # cleanup
            try:
                value_py = raw_value.replace('true', 'True').replace('false', 'False')
                value = ast.literal_eval(value_py)
            except Exception:
                value = raw_value.strip('"').strip("'")
            variables[var_name] = value
        else:
            variables[var_name] = None
    return variables


def parse_terraform_simple_assignments(file_content: str) -> dict:
    """
    Parse simple Terraform assignments of the form:
    name = value
    ignoring blocks.
    Returns dict of {variable_name: value}.
    """
    # Remove blocks first to avoid parsing duplicates
    no_blocks_content = re.sub(r'variable\s+"[^"]+"\s*{[^}]+}', '', file_content, flags=re.DOTALL)
    variables = {}
    simple_assignments = re.findall(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', no_blocks_content, re.MULTILINE)
    for var_name, raw_value in simple_assignments:
        raw_value = raw_value.strip().split('#')[0].strip()  # remove inline comment
        try:
            value_py = raw_value.replace('true', 'True').replace('false', 'False')
            value = ast.literal_eval(value_py)
        except Exception:
            value = raw_value.strip('"').strip("'")
        variables[var_name] = value
    return variables


# Example usage
if __name__ == "__main__":
    terraform_content = """
    variable "app_name" {
      description = "Name of the application"
      type        = string
      default     = "menu-management-backend"
    }

    region = "us-east-1"
    app_name = "menu-management-backend"
    environment = "production"
    database_url = "postgresql://user:password@host:5432/dbname"
    """

    block_vars = parse_terraform_blocks(terraform_content)
    simple_vars = parse_terraform_simple_assignments(terraform_content)

    print("Variables from blocks:")
    for k, v in block_vars.items():
        print(f"{k} = {v}")

    print("\nVariables from simple assignments:")
    for k, v in simple_vars.items():
        print(f"{k} = {v}")
