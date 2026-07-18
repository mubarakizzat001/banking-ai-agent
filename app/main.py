from api.router import master_router
from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference



app = FastAPI()
app.include_router(master_router)

@app.get("/scalar",include_in_schema=False)
async def scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title
    )