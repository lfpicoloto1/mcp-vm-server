# server.py
from typing import Dict, Any, List, Optional, Union
from mcp.server.fastmcp import FastMCP
import os
import requests
from pydantic import BaseModel

# Create an MCP server
mcp = FastMCP("VM Manager")

# Define models based on the swagger specification
class ID(BaseModel):
    id: str

class Name(BaseModel):
    name: str

class Network(BaseModel):
    vpc: Union[ID, Name]
    associate_public_ip: bool = True

class VMCreateRequest(BaseModel):
    name: str
    machine_type: Union[ID, Name]
    ssh_key_name: str
    image: Union[ID, Name]
    availability_zone: Optional[str] = None
    network: Optional[Network] = None
    user_data: Optional[str] = None

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

class CreateResponse(BaseModel):
    id: str
    name: str

# Configuration
API_BASE_URL = os.getenv("VM_API_URL", "https://api.magalu.cloud/br-se1/compute")
API_KEY = os.getenv("VM_API_KEY")

if not API_KEY:
    raise ValueError("VM_API_KEY environment variable is required")

# Add machine types listing tool
@mcp.tool()
def list_machine_types() -> Dict[str, Any]:
    """
    List all available machine types.
    
    Returns:
        Dict containing the list of machine types and pagination info
    """
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    params = {
        "_offset": 0,
        "_sort": "created_at:asc",
        "_limit": 100
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/v1/machine-types",
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

# Add images listing tool
@mcp.tool()
def list_images() -> Dict[str, Any]:
    """
    List all available images.
    
    Returns:
        Dict containing the list of images and pagination info
    """
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    params = {
        "_offset": 0,
        "_sort": "platform:asc,end_life_at:desc",
        "_limit": 100
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/v1/images",
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

# Add VM listing tool
@mcp.tool()
def list_vms() -> Dict[str, Any]:
    """
    List all virtual machines in the current tenant.
    
    Returns:
        Dict containing the list of VMs and pagination info
    """
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    params = {
        "_offset": 0,
        "_sort": "created_at:desc",
        "_limit": 100
    }
    
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

# Add VM creation tool
@mcp.tool()
def create_vm(
    name: str,
    machine_type_name: str,
    ssh_key_name: str,
    image_name: str,
    availability_zone: Optional[str] = None,
    vpc_id: Optional[str] = None,
    user_data: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new virtual machine.
    
    Args:
        name: Name of the VM
        machine_type_name: Name of the machine type
        ssh_key_name: Name of the SSH key to use
        image_name: Name of the image to use
        availability_zone: Optional availability zone
        vpc_id: Optional VPC ID
        user_data: Optional user data script (base64 encoded)
    
    Returns:
        Dict containing the VM creation response
    """
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": name,
        "machine_type": {"name": machine_type_name},
        "ssh_key_name": ssh_key_name,
        "image": {"name": image_name}
    }
    
    if availability_zone:
        payload["availability_zone"] = availability_zone
    
    if vpc_id:
        payload["network"] = {
            "vpc": {"id": vpc_id},
            "associate_public_ip": True
        }
    
    if user_data:
        payload["user_data"] = user_data
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/v1/instances",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "status_code": e.response.status_code if hasattr(e, 'response') else 500
        }

@mcp.tool()
def delete_vm(vm_id: str) -> Dict[str, Any]:
    """
    Delete a virtual machine.
    
    Args:
        vm_id: ID of the virtual machine to delete
    
    Returns:
        Dict containing the deletion response
    """
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/v1/instances/{vm_id}",
            headers=headers
        )
        response.raise_for_status()
        
        # For successful deletion, return empty dict as per typical DELETE endpoints
        if response.status_code == 204:
            return {"message": "VM deleted successfully"}
            
        return response.json()
        
    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "status_code": e.response.status_code if hasattr(e, 'response') else 500
        }

if __name__ == "__main__":
    mcp.run(transport="stdio")