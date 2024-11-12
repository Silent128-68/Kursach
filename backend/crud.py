from sqlalchemy.ext.asyncio import AsyncSession
from .models import PartType, Scheme, SchemePart

async def create_part_type(session: AsyncSession, name: str, type: str, quantity: int):
    new_part = PartType(name=name, type=type, quantity=quantity)
    session.add(new_part)
    await session.commit()
    await session.refresh(new_part)
    return new_part
