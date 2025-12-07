from server import app
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
    description="""
    API для хакатонов - участники и организаторы.
    
    ## Особенности авторизации:
    
    ### Для организаторов:
    1. Выполните **POST /api/organizer/login** с логином и паролем
    2. Сервер установит куки `access_token` и `user_id`
    3. Все последующие запросы будут автоматически использовать эти куки
    
    ### Тестирование в Swagger:
    - После входа скопируйте `access_token` из ответа
    - Нажмите **Authorize 🔒** вверху справа
    - Введите: `Bearer <ваш_token>`
    - Или используйте кнопку "Try it out" - браузер отправит куки
    
    ### Публичные эндпоинты:
    - Не требуют авторизации
    - Доступны для всех пользователей
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "persistAuthorization": True,  # Сохраняет авторизацию при обновлении
        "displayRequestDuration": True,  # Показывает время выполнения
        "docExpansion": "none",  # Сворачивает все блоки
    }
)

# CORS с поддержкой кук
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Укажите адрес фронтенда
    allow_credentials=True,  # Важно для кук!
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
        "api_prefix": API_PREFIX,
        "auth_info": {
            "type": "cookie-based (access_token) + Bearer token support",
            "login_endpoint": f"{API_PREFIX}/organizer/login",
            "register_endpoint": f"{API_PREFIX}/organizer/register",
            "note": "После входа токен сохраняется в куках браузера"
        },
        "endpoints": {
            "organizer": {
                "auth": f"{API_PREFIX}/organizer/login",
                "hackathons": f"{API_PREFIX}/organizer/hackathons",
                "teams": f"{API_PREFIX}/organizer/hackathons/{{id}}/teams",
            },
            "public": {
                "hackathons": f"{API_PREFIX}/public/hackathons",
                "teams": f"{API_PREFIX}/public/hackathons/{{id}}/teams",
                "participants": f"{API_PREFIX}/public/hackathons/{{id}}/participants"
            }
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, reload=True)