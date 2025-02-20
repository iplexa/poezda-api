from typing import Annotated
from fastapi import APIRouter

from repository import DirectionRepository
from schemas import SListDirection

router = APIRouter(prefix="/direction", tags=["Направления"])


@router.get('')
async def get_stations() -> SListDirection:
    directions = await DirectionRepository.get_directions()
    return {'directions': directions}
