from fastapi import Depends, FastAPI, HTTPException, security
from contextlib import asynccontextmanager
import uvicorn

from database import create_tables, delete_tables

from router import schedule_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print("База готова")
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(schedule_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
