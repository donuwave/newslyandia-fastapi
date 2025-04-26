from dataclasses import dataclass

from api_v1.contest.repository import ContestRepository


@dataclass
class ContestService:
    contest_repository: ContestRepository
