from mcp.server.fastmcp import FastMCP, Context
import httpx
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("Virtual Machines MCP API", dependencies=["httpx"])

API_BASE = "https://api.magalu.cloud/br-ne-1/compute/v1"


# Resources (GET endpoints)
@mcp.resource("vm://instances")
async def list_instances(ctx: Context, _limit: int = 50, _offset: int = 0, _sort: str = "created_at:asc", expand: list[str] = None, x_tenant_id: str = None) -> dict:
    """Lista todas as instâncias de VM do tenant atual."""
    params = {"_limit": _limit, "_offset": _offset, "_sort": _sort}
    if expand: params["expand"] = expand
    headers = {}
    if x_tenant_id: headers["x-tenant-id"] = x_tenant_id
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE}/instances", params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()

@mcp.resource("vm://images")
async def list_images(ctx: Context, _limit: int = 50, _offset: int = 0, _sort: str = "platform:asc,end_life_at:desc") -> dict:
    """Lista todas as imagens disponíveis para o tenant/região atual."""
    params = {"_limit": _limit, "_offset": _offset, "_sort": _sort}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE}/images", params=params)
        resp.raise_for_status()
        return resp.json()

@mcp.resource("vm://machine-types")
async def list_machine_types(ctx: Context, _limit: int = 50, _offset: int = 0, _sort: str = "created_at:asc") -> dict:
    """Lista todos os tipos de máquina disponíveis."""
    params = {"_limit": _limit, "_offset": _offset, "_sort": _sort}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE}/machine-types", params=params)
        resp.raise_for_status()
        return resp.json()

@mcp.resource("vm://snapshots")
async def list_snapshots(ctx: Context, _limit: int = 50, _offset: int = 0, _sort: str = "created_at:asc", expand: list[str] = None, x_tenant_id: str = None) -> dict:
    """Lista todos os snapshots do tenant atual."""
    params = {"_limit": _limit, "_offset": _offset, "_sort": _sort}
    if expand: params["expand"] = expand
    headers = {}
    if x_tenant_id: headers["x-tenant-id"] = x_tenant_id
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE}/snapshots", params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()

@mcp.resource("vm://backups")
async def list_backups(ctx: Context, _limit: int = 50, _offset: int = 0, _sort: str = "created_at:asc", expand: list[str] = None, x_tenant_id: str = None) -> dict:
    """Lista todos os backups do tenant atual."""
    params = {"_limit": _limit, "_offset": _offset, "_sort": _sort}
    if expand: params["expand"] = expand
    headers = {}
    if x_tenant_id: headers["x-tenant-id"] = x_tenant_id
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE}/backups", params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()

# Tools (ações)
@mcp.tool()
async def create_instance(ctx: Context, body: dict, x_tenant_id: str = None) -> dict:
    """Cria uma nova instância de VM."""
    headers = {"Content-Type": "application/json"}
    if x_tenant_id: headers["x-tenant-id"] = x_tenant_id
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/instances", json=body, headers=headers)
        resp.raise_for_status()
        return resp.json()

@mcp.tool()
async def delete_instance(ctx: Context, id: str, x_tenant_id: str = None, delete_public_ip: bool = False) -> dict:
    """Deleta uma instância de VM pelo id."""
    params = {"delete_public_ip": delete_public_ip}
    headers = {}
    if x_tenant_id: headers["x-tenant-id"] = x_tenant_id
    async with httpx.AsyncClient() as client:
        resp = await client.delete(f"{API_BASE}/instances/{id}", params=params, headers=headers)
        if resp.status_code == 204:
            return {"status": "deleted"}
        resp.raise_for_status()
        return resp.json()

@mcp.tool()
async def start_instance(ctx: Context, id: str, x_tenant_id: str = None) -> dict:
    """Inicia uma instância de VM pelo id."""
    headers = {}
    if x_tenant_id: headers["x-tenant-id"] = x_tenant_id
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/instances/{id}/start", headers=headers)
        if resp.status_code == 204:
            return {"status": "started"}
        resp.raise_for_status()
        return resp.json()

@mcp.tool()
async def stop_instance(ctx: Context, id: str, x_tenant_id: str = None) -> dict:
    """Para uma instância de VM pelo id."""
    headers = {}
    if x_tenant_id: headers["x-tenant-id"] = x_tenant_id
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/instances/{id}/stop", headers=headers)
        if resp.status_code == 204:
            return {"status": "stopped"}
        resp.raise_for_status()
        return resp.json()

@mcp.tool()
async def reboot_instance(ctx: Context, id: str, x_tenant_id: str = None) -> dict:
    """Reinicia uma instância de VM pelo id."""
    headers = {}
    if x_tenant_id: headers["x-tenant-id"] = x_tenant_id
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/instances/{id}/reboot", headers=headers)
        if resp.status_code == 204:
            return {"status": "rebooted"}
        resp.raise_for_status()
        return resp.json()

@mcp.tool()
async def suspend_instance(ctx: Context, id: str, x_tenant_id: str = None) -> dict:
    """Suspende uma instância de VM pelo id."""
    headers = {}
    if x_tenant_id: headers["x-tenant-id"] = x_tenant_id
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/instances/{id}/suspend", headers=headers)
        if resp.status_code == 204:
            return {"status": "suspended"}
        resp.raise_for_status()
        return resp.json()

@mcp.prompt()
def vm_query_prompt(query: str) -> list[base.Message]:
    return [
        base.UserMessage("Você deseja consultar ou operar máquinas virtuais."),
        base.UserMessage(f"Consulta: {query}"),
        base.AssistantMessage("Use os recursos vm://instances, vm://images, vm://machine-types, vm://snapshots, vm://backups ou as ferramentas para criar, deletar, iniciar, parar, reiniciar ou suspender VMs."),
    ]

if __name__ == "__main__":
    mcp.run() 