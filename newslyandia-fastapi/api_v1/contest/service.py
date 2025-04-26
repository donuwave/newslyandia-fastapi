from dataclasses import dataclass

from api_v1.contest.repository import ContestRepository
from api_v1.contest.schema import ContestRead, ContestCreate, ContestUpdate


@dataclass
class ContestService:
    contest_repository: ContestRepository

    async def get_contest(self, post_id: int) -> ContestRead:
        return await self.contest_repository.get_contest(post_id=post_id)

    async def get_contest_active(self) -> ContestRead:
        return await self.contest_repository.get_contest_active()

    async def create_contest(self, contest: ContestCreate):
        return await self.contest_repository.create_contest(contest=contest)

    async def update_contest(
        self,
        contest: ContestUpdate,
    ):
        return await self.contest_repository.update_contest(contest_data=contest)

    async def update_contest_deactivate(self):
        return await self.contest_repository.update_contest_deactivate()

    async def add_commentator(self, user_id: int):
        return await self.contest_repository.add_commentator(user_id=user_id)
