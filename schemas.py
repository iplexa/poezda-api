from pydantic import BaseModel, ConfigDict
from datetime import datetime, time

from sqlalchemy import Time


class SScheduleAdd(BaseModel):
    station: str
    direction: str
    time: time


class SScheduleCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    station_id: int
    direction_id: int
    time: time


class SSchedule(SScheduleCreate):
    uid: int


class SScheduleResponse(SScheduleAdd):
    uid: int


class SScheduleUid(BaseModel):
    uid: int


class SListSchedule(BaseModel):
    schedules: list[SScheduleResponse]


class SStation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: int
    name: str


class SListStation(BaseModel):
    stations: list[SStation]


class SDirection(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid: int
    direction: str


class SListDirection(BaseModel):
    directions: list[SDirection]


class SUserAdd(BaseModel):
    username: str
    password: str


class SUser(SUserAdd):
    uid: int


class SUserUuid(BaseModel):
    user_uid: int


class SUserLogin(SUserAdd):
    pass


class SUserAccessToken(BaseModel):
    token: str
