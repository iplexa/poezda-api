from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, Request

from repository import StationRepository
from schemas import SSchedule, SScheduleAdd, SScheduleUid, SListSchedule, SListStation

router = APIRouter(prefix="/station", tags=["Станции"])

@router.get('')
async def get_stations() -> SListStation:
    stations = await StationRepository.get_stations()
    return {'stations': stations}

