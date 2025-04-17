from mcp.server.fastmcp import FastMCP, Context
import httpx
from mcp.server.fastmcp.prompts import base
from typing import Optional, List

# Inicialização do MCP
mcp = FastMCP("Virtual Machines MCP API", dependencies=["httpx"])

# Constantes
API_BASE = "https://api.magalu.cloud/br-ne-1/compute/v1"

# Funções auxiliares
async def make_request(
    method: str,
    endpoint: str,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    json: Optional[dict] = None
) -> dict:
    """Realiza uma requisição HTTP para a API."""
    async with httpx.AsyncClient() as client:
        url = f"{API_BASE}/{endpoint}"
        response = await client.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            json=json
        )
        response.raise_for_status()
        return response.json() if response.status_code != 204 else {"status": "success"}

# Recursos (GET endpoints)
@mcp.resource("vm://instances")
async def list_instances(
    ctx: Context,
    limit: int = 50,
    offset: int = 0,
    sort: str = "created_at:asc",
    expand: Optional[List[str]] = None,
    x_tenant_id: Optional[str] = None
) -> dict:
    """Lista todas as instâncias de VM do tenant atual."""
    params = {"limit": limit, "offset": offset, "sort": sort}
    if expand:
        params["expand"] = expand
    headers = {}
    if x_tenant_id:
        headers["x-tenant-id"] = x_tenant_id
    return await make_request("GET", "instances", params=params, headers=headers)

@mcp.resource("vm://images")
async def list_images(
    ctx: Context,
    limit: int = 50,
    offset: int = 0,
    sort: str = "platform:asc,end_life_at:desc"
) -> dict:
    """Lista todas as imagens disponíveis para o tenant/região atual."""
    params = {"limit": limit, "offset": offset, "sort": sort}
    return await make_request("GET", "images", params=params)

@mcp.resource("vm://machine-types")
async def list_machine_types(
    ctx: Context,
    limit: int = 50,
    offset: int = 0,
    sort: str = "created_at:asc"
) -> dict:
    """Lista todos os tipos de máquina disponíveis."""
    params = {"limit": limit, "offset": offset, "sort": sort}
    return await make_request("GET", "machine-types", params=params)

@mcp.resource("vm://snapshots")
async def list_snapshots(
    ctx: Context,
    limit: int = 50,
    offset: int = 0,
    sort: str = "created_at:asc",
    expand: Optional[List[str]] = None,
    x_tenant_id: Optional[str] = None
) -> dict:
    """Lista todos os snapshots do tenant atual."""
    params = {"limit": limit, "offset": offset, "sort": sort}
    if expand:
        params["expand"] = expand
    headers = {}
    if x_tenant_id:
        headers["x-tenant-id"] = x_tenant_id
    return await make_request("GET", "snapshots", params=params, headers=headers)

@mcp.resource("vm://backups")
async def list_backups(
    ctx: Context,
    limit: int = 50,
    offset: int = 0,
    sort: str = "created_at:asc",
    expand: Optional[List[str]] = None,
    x_tenant_id: Optional[str] = None
) -> dict:
    """Lista todos os backups do tenant atual."""
    params = {"limit": limit, "offset": offset, "sort": sort}
    if expand:
        params["expand"] = expand
    headers = {}
    if x_tenant_id:
        headers["x-tenant-id"] = x_tenant_id
    return await make_request("GET", "backups", params=params, headers=headers)

# Ferramentas (ações)
@mcp.tool()
async def create_instance(
    ctx: Context,
    body: dict,
    x_tenant_id: Optional[str] = None
) -> dict:
    """Cria uma nova instância de VM."""
    headers = {"Content-Type": "application/json"}
    if x_tenant_id:
        headers["x-tenant-id"] = x_tenant_id
    return await make_request("POST", "instances", headers=headers, json=body)

@mcp.tool()
async def delete_instance(
    ctx: Context,
    id: str,
    x_tenant_id: Optional[str] = None,
    delete_public_ip: bool = False
) -> dict:
    """Deleta uma instância de VM pelo id."""
    params = {"delete_public_ip": delete_public_ip}
    headers = {}
    if x_tenant_id:
        headers["x-tenant-id"] = x_tenant_id
    return await make_request("DELETE", f"instances/{id}", params=params, headers=headers)

@mcp.tool()
async def start_instance(
    ctx: Context,
    id: str,
    x_tenant_id: Optional[str] = None
) -> dict:
    """Inicia uma instância de VM pelo id."""
    headers = {}
    if x_tenant_id:
        headers["x-tenant-id"] = x_tenant_id
    return await make_request("POST", f"instances/{id}/start", headers=headers)

@mcp.tool()
async def stop_instance(
    ctx: Context,
    id: str,
    x_tenant_id: Optional[str] = None
) -> dict:
    """Para uma instância de VM pelo id."""
    headers = {}
    if x_tenant_id:
        headers["x-tenant-id"] = x_tenant_id
    return await make_request("POST", f"instances/{id}/stop", headers=headers)

@mcp.tool()
async def reboot_instance(
    ctx: Context,
    id: str,
    x_tenant_id: Optional[str] = None
) -> dict:
    """Reinicia uma instância de VM pelo id."""
    headers = {}
    if x_tenant_id:
        headers["x-tenant-id"] = x_tenant_id
    return await make_request("POST", f"instances/{id}/reboot", headers=headers)

@mcp.tool()
async def suspend_instance(
    ctx: Context,
    id: str,
    x_tenant_id: Optional[str] = None
) -> dict:
    """Suspende uma instância de VM pelo id."""
    headers = {}
    if x_tenant_id:
        headers["x-tenant-id"] = x_tenant_id
    return await make_request("POST", f"instances/{id}/suspend", headers=headers)

# Prompt para consultas
@mcp.prompt()
def vm_query_prompt(query: str) -> List[base.Message]:
    """Gera o prompt para consultas de VM."""
    return [
        base.UserMessage("Você deseja consultar ou operar máquinas virtuais."),
        base.UserMessage(f"Consulta: {query}"),
        base.AssistantMessage(
            "Use os recursos vm://instances, vm://images, vm://machine-types, "
            "vm://snapshots, vm://backups ou as ferramentas para criar, deletar, "
            "iniciar, parar, reiniciar ou suspender VMs."
        ),
    ]

if __name__ == "__main__":
    mcp.run() 