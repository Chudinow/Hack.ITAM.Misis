from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Импортируем роутеры
from organize.routers.organizer_auth import router as organizer_auth_router
from organize.routers.organizer_hackathons import router as organizer_hackathons_router
from organize.routers.organizer_teams import router as organizer_teams_router
from organize.routers.public import router as public_router

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры для организаторов
app.include_router(organizer_auth_router, prefix=API_PREFIX)
app.include_router(organizer_hackathons_router, prefix=API_PREFIX)
app.include_router(organizer_teams_router, prefix=API_PREFIX)

# Подключаем публичные роутеры
app.include_router(public_router, prefix=API_PREFIX)

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
        },
        "public_endpoints": {
            "hackathons": f"{API_PREFIX}/public/hackathons",
            "teams": f"{API_PREFIX}/public/hackathons/{{id}}/teams",
            "participants": f"{API_PREFIX}/public/hackathons/{{id}}/participants"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, reload=True)