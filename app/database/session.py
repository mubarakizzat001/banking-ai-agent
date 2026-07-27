from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import settingDB

engine=create_async_engine(
    settingDB.async_db_url,echo=True
)
async def create_db():
    async with engine.begin() as conn:
        from database.models import Account,Customer,Transaction
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async_maker_session=sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_maker_session() as session:
        yield session
        
