from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from models import DetailTypes, Schemes, SchemeDetails
from pydantic import BaseModel
from typing import List
from base_class import Base
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal
from models import DetailTypes, Schemes, SchemeDetails
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


# Настройка асинхронного движка
DATABASE_URL = "postgresql+asyncpg://postgres:343424343424@localhost:5432/postgres"
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Создание асинхронной сессии
SessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Создание таблиц асинхронно
async def create_tables():
    async with engine.begin() as conn:
        # Используем асинхронный метод для создания таблиц
        await conn.run_sync(Base.metadata.create_all)

# Инициализация FastAPI
app = FastAPI()

# Middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создание таблиц при старте приложения
@app.on_event("startup")
async def startup():
    await create_tables()

class DetailTypeCreate(BaseModel):
    name: str
    type: str
    quantity: int

class SchemeCreate(BaseModel):
    scheme_name: str

class SchemeDetailCreate(BaseModel):
    scheme_id: int
    detail_type_id: int
    quantity: int

class QuantityUpdate(BaseModel):
    quantity: int

class DetailRequest(BaseModel):
    detail_type_id: int
    quantity: int

# Асинхронная функция для получения сессии
async def get_db():
    async with SessionLocal() as session:
        yield session

# Создание нового типа детали
@app.post("/detail_types", response_model=DetailTypeCreate)
async def create_detail_type(detail_type: DetailTypeCreate, db: AsyncSession = Depends(get_db)):
    db_detail_type = DetailTypes(**detail_type.dict())
    db.add(db_detail_type)
    await db.commit()  # Асинхронный commit
    await db.refresh(db_detail_type)  # Асинхронный refresh
    return db_detail_type

# Создание новой схемы
@app.post("/schemes", response_model=SchemeCreate)
async def create_scheme(scheme: SchemeCreate, db: AsyncSession = Depends(get_db)):
    db_scheme = Schemes(**scheme.dict())
    db.add(db_scheme)
    await db.commit()  # Асинхронный commit
    await db.refresh(db_scheme)  # Асинхронный refresh
    return db_scheme

# Создание новой схемы детали
@app.post("/scheme_details", response_model=SchemeDetailCreate)
async def create_scheme_detail(scheme_detail: SchemeDetailCreate, db: AsyncSession = Depends(get_db)):
    db_scheme_detail = SchemeDetails(**scheme_detail.dict())
    db.add(db_scheme_detail)
    await db.commit()  # Асинхронный commit
    await db.refresh(db_scheme_detail)  # Асинхронный refresh
    return db_scheme_detail

# Функция для добавления детали к схеме
@app.post("/schemes/{scheme_id}/add_detail")
async def add_detail_to_scheme(scheme_id: int, detail: DetailRequest, db: AsyncSession = Depends(get_db)):
    detail_type_id = detail.detail_type_id
    quantity = detail.quantity

    # Проверяем, что схема существует
    async with db.begin():
        result = await db.execute(select(Schemes).filter(Schemes.id == scheme_id))
        scheme = result.scalars().first()

        if not scheme:
            raise HTTPException(status_code=404, detail="Scheme not found")

        # Проверяем, что тип детали существует
        result = await db.execute(select(DetailTypes).filter(DetailTypes.id == detail_type_id))
        detail_type = result.scalars().first()

        if not detail_type:
            raise HTTPException(status_code=404, detail="Detail type not found")

        # Проверяем, существует ли запись в таблице SchemeDetails
        scheme_detail = await db.execute(
            select(SchemeDetails).filter(
                SchemeDetails.scheme_id == scheme_id,
                SchemeDetails.detail_type_id == detail_type_id
            )
        )
        scheme_detail = scheme_detail.scalars().first()

        if scheme_detail:
            # Если запись существует, обновляем количество
            scheme_detail.quantity += quantity
        else:
            # Если записи нет, создаём новую запись
            scheme_detail = SchemeDetails(scheme_id=scheme_id, detail_type_id=detail_type_id, quantity=quantity)
            db.add(scheme_detail)

        await db.commit()  # Сохраняем изменения в базе данных

        return {"scheme_id": scheme.id, "detail_type_id": detail_type.id, "quantity": scheme_detail.quantity}

@app.get("/detail_types")
async def get_detail_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DetailTypes))
    return result.scalars().all()

@app.get("/schemes")
async def get_schemes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Schemes))
    return result.scalars().all()

@app.get("/schemes/{scheme_id}/details")
async def get_details_for_scheme(scheme_id: int, db: AsyncSession = Depends(get_db)):
    # Ищем схему по ID и загружаем связанные детали через SchemeDetails
    result = await db.execute(select(Schemes).filter(Schemes.id == scheme_id).options(selectinload(Schemes.scheme_details).selectinload(SchemeDetails.detail_type)))
    scheme = result.scalar_one_or_none()

    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Возвращаем список деталей для схемы
    return [
        {"name": detail.detail_type.name, "quantity": detail.quantity, "type": detail.detail_type.type}
        for detail in scheme.scheme_details
    ]

@app.delete("/detail_types/{detail_type_id}")
async def delete_detail_type(detail_type_id: int, db: AsyncSession = Depends(get_db)):
    # Ищем тип детали по ID
    result = await db.execute(select(DetailTypes).filter(DetailTypes.id == detail_type_id))
    detail_type = result.scalar_one_or_none()
    
    # Если тип детали не найден, выбрасываем ошибку
    if not detail_type:
        raise HTTPException(status_code=404, detail="Detail type not found")

    # Удаляем тип детали
    await db.delete(detail_type)
    await db.commit()  # Сохраняем изменения в БД

    return {"message": "Detail type deleted successfully"}

@app.delete("/schemes/{scheme_id}")
async def delete_scheme(scheme_id: int, db: AsyncSession = Depends(get_db)):
    # Найти схему по ID
    scheme = await db.get(Schemes, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Удалить схему (автоматически удалит связанные записи из scheme_details)
    await db.delete(scheme)
    await db.commit()
    return {"detail": "Scheme and its details deleted successfully"}

# Асинхронная функция для добавления количества
@app.put("/detail_types/{detail_type_id}/add")
async def add_quantity(detail_type_id: int, quantity_update: QuantityUpdate, db: AsyncSession = Depends(get_db)):
    # Используем select для асинхронного запроса
    async with db.begin():
        result = await db.execute(select(DetailTypes).filter(DetailTypes.id == detail_type_id))
        detail_type = result.scalars().first()  # Получаем первый результат

        if not detail_type:
            raise HTTPException(status_code=404, detail="Detail type not found")

        # Обновляем количество
        detail_type.quantity += quantity_update.quantity
        await db.commit()  # Сохраняем изменения в базе данных

        # Возвращаем обновленные данные
        return {
            "id": detail_type.id,
            "name": detail_type.name,
            "quantity": detail_type.quantity,
            "type": detail_type.type
        }