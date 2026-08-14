from sqlmodel import SQLModel
from database.session import get_session
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from main import app
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import databseconfig

test_settingDB = databseconfig(
    postgres_server="localhost",
    postgres_port=5433,
    postgres_user="postgres",
    postgres_password="postgres",
    postgres_db="banking_test",
)
test_engine=create_async_engine(
    url=test_settingDB.async_db_url,
    echo=True
)

test_async_sessionmaker=sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
async def get_session_override():
    async with test_async_sessionmaker() as session:
        yield session

@pytest_asyncio.fixture(scope="session")
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client




@pytest.fixture(scope="function",autouse=True)
async def setup_teardown():
    print("setting up")
    
    app.dependency_overrides[get_session]=get_session_override
    async with test_engine.begin() as conn:
        from database.models import Account,Customer,Transaction,UserAccounts
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    
    async with test_engine.begin() as conn:

        await conn.run_sync(SQLModel.metadata.drop_all)
    print(test_engine.url)
    app.dependency_overrides.clear()
    print("tearing down")