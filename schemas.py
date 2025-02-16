from pydantic import BaseModel
from datetime import datetime, time


class SScheduleAdd(BaseModel):
    station_uid: str
    direction_uid: str
    time: time


class SScheduleCreate(BaseModel):
    station_id: int
    direction_id: int
    time: time


class SSchedule(SScheduleCreate):
    uid: int


class SScheduleUid(BaseModel):
    uid: int


class SListSchedule(BaseModel):
    schedules: list[SSchedule]


class SStation(BaseModel):
    uid: int
    name: str


class SDirection(BaseModel):
    uid: int
    direction: str


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
