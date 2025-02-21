from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

import os

from contextlib import asynccontextmanager

import uvicorn

from database import create_tables, delete_tables

from router import schedule_router, station_router, direction_router
from admin import router as admin_router
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await delete_tables()
    # print("База очищена")
    await create_tables()
    print("База готова")
    yield


app = FastAPI(lifespan=lifespan, root_path='/api')
app.include_router(schedule_router)
app.include_router(station_router)
app.include_router(direction_router)
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session configuration
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "supersecretkey"),
    session_cookie="admin_session",
    max_age=3600  # 1 hour session
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    from admin import recent_requests
    request_data = {
        "ip": request.client.host,
        "method": request.method,
        "path": request.url.path,
        "timestamp": datetime.now().isoformat()
    }
    recent_requests.append(request_data)
    if len(recent_requests) > 100:  # Keep only last 100 requests
        recent_requests.pop(0)

    response = await call_next(request)
    return response


if __name__ == "__main__":
    uvicorn.run('main:app', reload=True)
