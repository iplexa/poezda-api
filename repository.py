from typing import List

from fastapi import HTTPException
from sqlalchemy import select

from database import new_session, ScheduleOrm, StationOrm, DirectionOrm
from schemas import SSchedule, SScheduleAdd, SStation, SDirection, SScheduleCreate, SScheduleResponse


class ScheduleRepository:
    @classmethod
    async def get_schedules(cls) -> list[SScheduleResponse]:
        async with new_session() as session:
            query = (
                select(
                    ScheduleOrm.uid,
                    StationOrm.name,
                    DirectionOrm.direction,
                    ScheduleOrm.time
                )
                .outerjoin(StationOrm, ScheduleOrm.station_id == StationOrm.uid)
                .outerjoin(DirectionOrm, ScheduleOrm.direction_id == DirectionOrm.uid)
            )
            result = await session.execute(query)
            schedule_models = result.all()
            # print(schedule_models)
            schedule_info = [
                SScheduleResponse(uid=uid, station=station, direction=direction, time=time)
                for uid, station, direction, time in schedule_models
            ]
            # schedule_schemas = [
            #     SScheduleResponse.model_validate(schedule_model)
            #     for schedule_model in schedule_models
            # ]
            return schedule_info

    @classmethod
    async def create_schedule(cls, data: SScheduleCreate) -> int:
        async with new_session() as session:
            schedule_dict = data.model_dump()
            new_schedule = ScheduleOrm(**schedule_dict)
            session.add(new_schedule)
            await session.flush()
            await session.commit()
            return new_schedule.uid

    @classmethod
    async def put_schedule(cls, uid: int, data: SScheduleCreate) -> None:
        async with new_session() as session:
            query = select(ScheduleOrm).where(ScheduleOrm.uid == uid)
            result = await session.execute(query)
            schedule_model = result.scalars().first()
            if schedule_model is None:
                raise HTTPException(status_code=404, detail="No such schedule")

            schedule_dict = data.model_dump()
            new_schedule = ScheduleOrm(**schedule_dict)

            await session.delete(result)
            await session.add(new_schedule)
            await session.flush()
            await session.commit()

            return

    @classmethod
    async def delete_schedule(cls, uid: int) -> None:
        async with new_session() as session:
            query = select(ScheduleOrm).where(ScheduleOrm.uid == uid)
            result = await session.execute(query)
            await session.delete(result)
            await session.commit()
            return

class StationRepository:
    @classmethod
    async def get_stations(cls) -> List[SStation]:
        async with new_session() as session:
            query = select(StationOrm)
            result = await session.execute(query)
            stations_models = result.scalars().all()
            station_schemas = [
                SStation.model_validate(stations_model)
                for stations_model in stations_models
            ]
            return station_schemas

    @classmethod
    async def get_station_by_id(cls, uid: int) -> SStation:
        async with new_session() as session:
            query = select(StationOrm).where(StationOrm.uid == uid)
            result = await session.execute(query)
            stations_model = result.scalars().first()
            if stations_model is None:
                raise HTTPException(status_code=404, detail="No such station")
            station_schema = SStation.model_validate(stations_model)
            return station_schema

    @classmethod
    async def get_station_by_name(cls, name: str) -> SStation:
        async with new_session() as session:
            query = select(StationOrm).where(StationOrm.name == name)
            result = await session.execute(query)
            stations_model = result.scalars().first()
            if stations_model is None:
                raise HTTPException(status_code=404, detail="No such station")
            station_schema = SStation.from_orm(stations_model)
            return station_schema


class DirectionRepository:
    @classmethod
    async def get_directions(cls, uid: int) -> List[SDirection]:
        async with new_session() as session:
            query = select(DirectionOrm).where(DirectionOrm.uid == uid)
            result = await session.execute(query)
            directions_models = result.scalars().all()
            directions_schemas = [
                SDirection.model_validate(directions_model)
                for directions_model in directions_models
            ]
            return directions_schemas

    @classmethod
    async def get_direction_by_id(cls, uid: int) -> SDirection:
        async with new_session() as session:
            query = select(DirectionOrm).where(DirectionOrm.uid == uid)
            result = await session.execute(query)
            directions_model = result.scalars().first()
            if directions_model is None:
                raise HTTPException(status_code=404, detail="No such direction")
            direction_schema = SDirection.model_validate(directions_model)
            return direction_schema

    @classmethod
    async def get_direction_by_name(cls, direction: str) -> SDirection:
        async with new_session() as session:
            query = select(DirectionOrm).where(DirectionOrm.direction == direction)
            result = await session.execute(query)
            directions_model = result.scalars().first()
            if directions_model is None:
                raise HTTPException(status_code=404, detail="No such direction")
            direction_schema = SDirection.model_validate(directions_model)
            return direction_schema


# class UserRepository:
#     @classmethod
#     async def add_user(cls, data: SUserAdd) -> int:
#         async with new_session() as session:
#             user_dict = data.model_dump()
#
#             new_user = UserOrm(**user_dict)
#             session.add(new_user)
#
#             await session.flush()
#             await session.commit()
#
#             return new_user.uid  # Change from new_user.id to new_user.uid
#
#     @classmethod
#     async def get_users(cls) -> list[SUser]:
#         async with new_session() as session:
#             query = select(UserOrm)
#             result = await session.execute(query)
#             user_models = result.scalars().all()
#             user_schemas = [
#                 SUser.model_validate(user_model) for user_model in user_models
#             ]
#             return user_schemas
#
#     @classmethod
#     async def get_user(cls, all: bool = False, **user_fields) -> SUser | list[SUser]:
#         async with new_session() as session:
#             query = select(UserOrm)
#
#             if user_fields:
#                 for field_name, field_value in user_fields.items():
#                     query = query.where(getattr(UserOrm, field_name) == field_value)
#
#             result = await session.execute(query)
#             user_models = result.scalars().all()
#
#             if all:
#                 return [
#                     SUser.model_validate(user_model.__dict__)
#                     for user_model in user_models
#                 ]
#             else:
#                 return (
#                     SUser.model_validate(user_models[0].__dict__)
#                     if user_models
#                     else None
#                 )
#
#     @classmethod
#     async def login_user(cls, creds: SUserLogin) -> SUser | None:
#         async with new_session() as session:
#             query = select(UserOrm).where(UserOrm.username == creds.username)
#             result = await session.execute(query)
#             user_model = result.scalars().first()
#             if user_model:
#                 if user_model.password == creds.password:
#                     return user_model.uid
#                 else:
#                     return None
#             else:
#                 return None
