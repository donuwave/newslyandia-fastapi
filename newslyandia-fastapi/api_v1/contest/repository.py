from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ContestRepository:
    db_session: AsyncSession
