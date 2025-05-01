from dataclasses import dataclass

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import Contest
from api_v1.contest.schema import ContestRead, ContestCreate, ContestUpdate


@dataclass
class ContestRepository:
    db_session: AsyncSession

    async def get_contest_list(self):
        stmt = select(Contest).order_by(Contest.id.desc())
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_contest(self, post_id: int) -> ContestRead:
        query = select(Contest).where(Contest.post_id == post_id)

        session = await self.db_session.execute(query)
        return session.scalar()

    async def get_contest_active(self) -> ContestRead:
        query = select(Contest).where(Contest.is_active == True)

        session = await self.db_session.execute(query)
        return session.scalar()

    async def add_commentator(self, user_id: int):
        result = await self.db_session.execute(
            select(Contest).where(Contest.is_active == True)
        )
        contest = result.scalars().first()

        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")

        if user_id not in contest.commentators:
            contest.commentators = contest.commentators + [user_id]

        self.db_session.add(contest)
        await self.db_session.commit()
        await self.db_session.refresh(contest)
        await self.db_session.close()

    async def create_contest(self, contest: ContestCreate):
        contest_obj = Contest(**contest.model_dump())

        stmt = select(Contest).where(Contest.post_id == contest_obj.post_id)
        result = await self.db_session.execute(stmt)
        duplicate = result.scalars().first()

        if duplicate:
            raise HTTPException(
                status_code=409, detail="Contest already exists for this post"
            )

        self.db_session.add(contest_obj)
        await self.db_session.commit()
        await self.db_session.refresh(contest_obj)
        return contest_obj

    async def update_contest(self, contest_data: ContestUpdate):
        stmt = select(Contest).where(Contest.post_id == contest_data.post_id)
        result = await self.db_session.execute(stmt)
        contest = result.scalars().first()

        if contest is None:
            raise HTTPException(status_code=404, detail="Contest not found")

        update_data = contest_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contest, field, value)

        await self.db_session.commit()
        await self.db_session.refresh(contest)
        return contest

    async def update_contest_deactivate(self):
        stmt = select(Contest).where(Contest.is_active == True)
        result = await self.db_session.execute(stmt)
        contest = result.scalars().first()

        if contest is None:
            raise HTTPException(status_code=404, detail="Contest not found")

        contest.is_active = False

        self.db_session.add(contest)
        await self.db_session.commit()
        await self.db_session.refresh(contest)
        await self.db_session.close()
