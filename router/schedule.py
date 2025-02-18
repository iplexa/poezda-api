import time
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy import Time

from repository import ScheduleRepository, StationRepository, DirectionRepository
from schemas import (
    SSchedule,
    SScheduleAdd,
    SScheduleUid,
    SListSchedule,
    SScheduleCreate,
    SStation,
)

router = APIRouter(prefix="/api/schedule", tags=["Расписание"])


@router.post("/add")
async def add_schedule(schedule: Annotated[SScheduleAdd, Depends()]) -> SScheduleUid:
    station: SStation = await StationRepository.get_station_by_name(schedule.station)
    station_id = station.uid
    if not station_id:
        raise HTTPException(404, "No such station")
    direction = await DirectionRepository.get_direction_by_name(schedule.direction)
    direction_id = direction.uid
    if not direction_id:
        raise HTTPException(404, "No such direction")
    db_add_schedule = SScheduleCreate(
        station_id=station_id,
        direction_id=direction_id,
        time=schedule.time,
    )
    schedule_uid = await ScheduleRepository.create_schedule(db_add_schedule)
    return {"uid": schedule_uid}


@router.get("")
async def get_schedule() -> SListSchedule:
    schedules = await ScheduleRepository.get_schedules()
    return {"schedules": schedules}


@router.put("/update")
async def update_schedule(
    uid: Annotated[SScheduleUid, Depends()],
    schedule: Annotated[SScheduleCreate, Depends()],
) -> None:
    await ScheduleRepository.put_schedule(uid.uid, schedule)
    return

@router.delete("/delete")
async def delete_schedule(uid: Annotated[SScheduleUid, Depends()]) -> None:
    await ScheduleRepository.delete_schedule(uid.uid)
    return
