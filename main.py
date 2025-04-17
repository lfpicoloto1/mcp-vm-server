# server.py
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP
import os
import requests
from pydantic import BaseModel

# Create an MCP server
mcp = FastMCP("VM Manager")

# Define models based on the swagger specification
class VM(BaseModel):
    id: str
    name: str
    status: str
    state: str
    created_at: str
    updated_at: str
    flavor: Dict[str, Any]
    image: Dict[str, Any]
    networks: List[Dict[str, Any]]

class ListVMResponse(BaseModel):
    vms: List[VM]
    total: int
    limit: int
    offset: int

# Configuration
API_BASE_URL = os.getenv("VM_API_URL", "https://api.magalu.cloud/br-ne-1/compute")
API_KEY = os.getenv("VM_API_KEY")
API_BASE_URL = "https://api.magalu.cloud/br-se1/compute{}".format(API_KEY)
if not API_KEY:
    raise ValueError("VM_API_KEY environment variable is required")

# Add VM listing tool
@mcp.tool()
def list_vms(
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    sort: Optional[str] = "created_at:asc",
    expand: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    List all virtual machines in the current tenant.
    
    Args:
        limit: Maximum number of results to return (default: 50)
        offset: Number of results to skip (default: 0)
        sort: Sort order (default: "created_at:asc")
        expand: List of fields to expand in the response
    
    Returns:
        Dict containing the list of VMs and pagination info
    """
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    params = {
        "_limit": limit,
        "_offset": offset,
        "_sort": sort
    }
    
    if expand:
        params["expand"] = expand
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/v1/instances",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "status_code": e.response.status_code if hasattr(e, 'response') else 500
        }

# Add VM details tool
@mcp.tool()
def get_vm(vm_id: str) -> Dict[str, Any]:
    """
    Get details of a specific virtual machine.
    
    Args:
        vm_id: ID of the virtual machine to get details for
    
    Returns:
        Dict containing the VM details
    """
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/v1/instances/{vm_id}",
            headers=headers
        )
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "status_code": e.response.status_code if hasattr(e, 'response') else 500
        }

if __name__ == "__main__":
    mcp.run(transport="stdio")