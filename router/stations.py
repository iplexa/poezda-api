from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, Request

from repository import StationRepository
from schemas import SSchedule, SScheduleAdd, SScheduleUid, SListSchedule

router = APIRouter(prefix="/api/station", tags=["Станции"])
