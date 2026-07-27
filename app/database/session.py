from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settingDB

engine=create_async_engine(
    settingDB.async_db_url,echo=True
)
async def create_db():
    async with engine.begin() as conn:
        from .models import transactions
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_seesion():
    async_maker_session=sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_maker_session() as session:
        yield session
        
