# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Импортируем НАШИ роутеры
from routers import (
    organizer_auth_router,
    organizer_hackathons_router,
    organizer_teams_router
)

from db import db
from config import API_PREFIX

app = FastAPI(
    title="Hackathon Platform API",
    description="API для хакатонов - участники и организаторы",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В проде укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем НАШИ роутеры для организаторов
app.include_router(organizer_auth_router, prefix=API_PREFIX)
app.include_router(organizer_hackathons_router, prefix=API_PREFIX)
app.include_router(organizer_teams_router, prefix=API_PREFIX)

# Создаем папку для загрузок если не существует
os.makedirs("uploads/hackathon_photos", exist_ok=True)


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


@app.get("/")
async def root():
    return {
        "message": "Hackathon Platform API",
        "docs": "/docs",
        "organizer_endpoints": {
            "auth": f"{API_PREFIX}/organizer/login",
            "hackathons": f"{API_PREFIX}/organizer/hackathons",
            "teams": f"{API_PREFIX}/organizer/hackathons/{{id}}/teams",
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)