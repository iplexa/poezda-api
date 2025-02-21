from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Response
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
import logging
from typing import List, Dict, AsyncGenerator
from datetime import datetime
from database import get_db
from sqlalchemy import inspect, text, update
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib
from repository import TableRepository

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/admin", tags=["Admin"])
security = HTTPBasic()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log"
)

# In-memory storage for recent requests
recent_requests = []

# Password for admin access
ADMIN_PASSWORD = "adminadmin"  # TODO: Move to environment variables


async def verify_password(request: Request):
    session = request.session.get("admin_auth")
    if not session or session != hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest():
        return False
    return True


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


from fastapi import Body


@router.post("/login")
async def login(request: Request, password: str = Body(..., embed=True)):
    if password == ADMIN_PASSWORD:
        request.session["admin_auth"] = hashlib.sha256(password.encode()).hexdigest()
        return RedirectResponse(url="/api/admin", status_code=status.HTTP_303_SEE_OTHER)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect password"
    )


@router.get("/check-session")
async def check_session(request: Request):
    """Check if admin session is valid"""
    if await verify_password(request):
        return {"status": "valid"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Session expired or invalid"
    )


@router.get("/logs")
async def get_logs(_: str = Depends(verify_password)):
    """Get application logs"""
    try:
        with open("app.log", "r") as log_file:
            logs = log_file.readlines()
        return {"logs": logs}
    except FileNotFoundError:
        return {"logs": []}


@router.get("/requests")
async def get_recent_requests(_: str = Depends(verify_password)):
    """Get recent requests"""
    return {"requests": recent_requests}


@router.get("")
async def admin_page(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    if not await verify_password(request):
        return RedirectResponse(url="/api/admin/login")

    try:
        with open("app.log", "r") as log_file:
            logs = log_file.read()
    except FileNotFoundError:
        logs = "No logs available"

    async with db.begin() as transaction:
        connection = await db.connection()

        def sync_inspect(conn):
            inspector = inspect(conn)
            return inspector.get_table_names(schema="public")

        table_names = await connection.run_sync(sync_inspect)
        tables = [{"name": table_name} for table_name in table_names]

    serialized_tables = [dict(table) for table in tables]

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "logs": logs,
            "requests": recent_requests,
            "tables": serialized_tables
        }
    )


@router.get("/tables/{table_name}")
async def view_table(
        table_name: str,
        _: str = Depends(verify_password),
        db: AsyncSession = Depends(get_db)
):
    """View contents of a database table"""
    return await TableRepository.get_table_data(table_name, db)


@router.post("/tables/{table_name}/edit")
async def edit_table(
        table_name: str,
        data: Dict[str, str],
        _: str = Depends(verify_password),
        db: AsyncSession = Depends(get_db)
):
    """Edit contents of a database table"""
    return await TableRepository.update_table_row(table_name, data, db)


@router.post("/tables/{table_name}/create")
async def create_table_row(
        table_name: str,
        data: Dict[str, str],
        _: str = Depends(verify_password),
        db: AsyncSession = Depends(get_db)
):
    """Create a new row in a database table"""
    return await TableRepository.create_table_row(table_name, data, db)


@router.post("/add-schedule")
async def add_schedule(
        request: Request,
        schedule_data: str = Body(..., embed=True),
        db: AsyncSession = Depends(get_db),
        _: str = Depends(verify_password)
):
    """Add new schedule entries from a formatted string"""
    try:
        # Разделяем строку на отдельные записи
        entries = schedule_data.strip().split("\n")

        for entry in entries:
            # Парсим время и описание
            time_part, description = entry.split(maxsplit=1)

            # Обрабатываем время (если есть диапазон, берем первое время)
            if '-' in time_part:
                time_part = time_part.split('-')[0]

            # Преобразуем время в формат HH:MM:SS
            time_obj = datetime.strptime(time_part, "%H:%M").time()

            # Определяем направление (Север или Юг)
            if "в сторону Ховрино" in description or "на север" in description:
                direction_id = 1  # Север
            elif "в сторону Алма-Атинской" in description or "на юг" in description:
                direction_id = 2  # Юг
            else:
                # Если направление не указано, считаем его северным по умолчанию
                direction_id = 1

            # Определяем станцию
            station_name = None
            for station in ["Ховрино", "Беломорская", "Речной вокзал", "Водный стадион", "Войковская", "Сокол",
                            "Аэропорт", "Динамо", "Белорусская", "Маяковская", "Тверская", "Театральная",
                            "Новокузнецкая", "Павелецкая", "Автозаводская", "Технопарк", "Коломенская",
                            "Каширская", "Кантемировская", "Царицыно", "Орехово", "Домодедовская",
                            "Красногвардейская", "Алма-Атинская"]:
                if station in description:
                    station_name = station
                    break

            if not station_name:
                raise HTTPException(status_code=400, detail=f"Не удалось определить станцию для записи: {entry}")

            # Получаем ID станции
            station_query = await db.execute(select(StationOrm).where(StationOrm.name == station_name))
            station = station_query.scalars().first()
            if not station:
                raise HTTPException(status_code=400, detail=f"Станция '{station_name}' не найдена в базе данных")

            # Создаем новую запись в расписании
            new_schedule = ScheduleOrm(
                time=time_obj,
                station_id=station.uid,
                direction_id=direction_id
            )
            db.add(new_schedule)

        await db.commit()
        return {"status": "success", "message": "Расписание успешно добавлено"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
