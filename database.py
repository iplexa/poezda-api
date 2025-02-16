from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Time
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_async_engine(
    "postgresql+asyncpg://poezda:poezda@vpn.iplexa.site/poezda",
)

new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass


class UserOrm(Model):
    __tablename__ = "users"
    telegram_id = Column(Integer, primary_key=True)


class StationOrm(Model):
    __tablename__ = "stations"
    uid: Mapped[int] = mapped_column(primary_key=True)
    name = Column(String, unique=True)


class DirectionOrm(Model):
    __tablename__ = "directions"
    uid: Mapped[int] = mapped_column(primary_key=True)
    direction = Column(String)


class ScheduleOrm(Model):
    __tablename__ = "schedules"
    uid: Mapped[int] = mapped_column(primary_key=True)
    time = Column(Time)
    station_id = Column(Integer, ForeignKey("stations.uid"))
    direction_id = Column(Integer, ForeignKey("directions.uid"))


class SubscriptionOrm(Model):
    __tablename__ = "subscriptions"
    uid: Mapped[int] = mapped_column(primary_key=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id"))
    station_id = Column(Integer, ForeignKey("stations.uid"))


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
