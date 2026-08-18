from fastapi import FastAPI
from httpx import AsyncClient,ASGITransport


_client:AsyncClient | None = None

async def init_client(app:FastAPI):
    global _client
    if _client is None:
        _client = AsyncClient(transport=ASGITransport(app=app),
        base_url="http://localhost"
        )
    return _client

def get_client() -> AsyncClient:
    if _client is None:
        raise RuntimeError("Client not initialized. Call init_client first.")
    return _client

async def close_client():
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None

  