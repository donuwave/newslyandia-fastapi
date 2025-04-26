from fastapi import APIRouter

router = APIRouter(tags=["contest"])


@router.get("")
async def get_contest():
    return
