from multiprocessing.managers import Array
from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from .dependency import get_contest_service
from .schema import ContestRead, ContestCreate, ContestUpdate
from .service import ContestService

router = APIRouter(tags=["contest"])


@router.get("", response_model=Array(ContestRead))
async def get_contest_list(
    contest_service: Annotated[ContestService, Depends(get_contest_service)],
):
    return await contest_service.get_contest_list()


@router.get("/{post_id}", response_model=ContestRead)
async def get_contest(
    post_id: int,
    contest_service: Annotated[ContestService, Depends(get_contest_service)],
):
    return await contest_service.get_contest(post_id=post_id)


@router.post("/active", response_model=ContestRead)
async def get_contest_active(
    contest_service: Annotated[ContestService, Depends(get_contest_service)],
):
    return await contest_service.get_contest_active()


@router.post("")
async def create_contest(
    contest: ContestCreate,
    contest_service: Annotated[ContestService, Depends(get_contest_service)],
):
    return await contest_service.create_contest(contest=contest)


@router.patch("/{post_id}")
async def update_contest(
    contest: ContestUpdate,
    contest_service: Annotated[ContestService, Depends(get_contest_service)],
):
    return await contest_service.update_contest(contest=contest)


@router.post("/deactivate")
async def update_contest_deactivate(
    contest_service: Annotated[ContestService, Depends(get_contest_service)],
):
    return await contest_service.update_contest_deactivate()


@router.post("/active/add_commentator/{user_id}")
async def add_commentator(
    user_id: int,
    contest_service: Annotated[ContestService, Depends(get_contest_service)],
):
    return await contest_service.add_commentator(user_id=user_id)
