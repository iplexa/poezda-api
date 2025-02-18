from fastapi import Depends, FastAPI, HTTPException, security
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
import uvicorn

from database import create_tables, delete_tables

from router import schedule_router, station_router, direction_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await delete_tables()
    # print("База очищена")
    await create_tables()
    print("База готова")
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(schedule_router)
app.include_router(station_router)
app.include_router(direction_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
