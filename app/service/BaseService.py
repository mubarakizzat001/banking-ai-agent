from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel


class BaseService:

    def __init__(self,model:SQLModel,session:AsyncSession):
        self.model=model
        self.session=session

    async def _get(self,id:int):
        return await self.session.get(self.model,id)

    async def _create(self,data:SQLModel):
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def _update(self,data:SQLModel):
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def _delete(self,data:SQLModel):
        await self.session.delete(data)
        await self.session.commit()
        return True