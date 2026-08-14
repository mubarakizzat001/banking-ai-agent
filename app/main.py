from api.router import master_router
from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from database.session import create_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(master_router)

@app.get("/",include_in_schema=False)
async def root():
    return {"message":"server is running!"}

@app.get("/scalar",include_in_schema=False)
async def scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title
    )