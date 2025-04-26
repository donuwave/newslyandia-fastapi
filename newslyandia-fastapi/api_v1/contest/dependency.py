from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.contest.repository import ContestRepository
from api_v1.contest.service import ContestService
from config.database import db_helper


async def get_contest_repository(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> ContestRepository:
    return ContestRepository(db_session=session)


async def get_contest_service(
    contest_repository: ContestRepository = Depends(get_contest_repository),
) -> ContestService:
    return ContestService(contest_repository=contest_repository)
