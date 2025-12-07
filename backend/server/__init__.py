from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import db
from server.mw import ErrorHandlerMiddleware
from server.routes import hack_router, team_router, user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(
    title="Hack.ITAM.Misis API",
    description="API для хакатона МИСИС",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # На хакатоне разрешаем всем
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ErrorHandlerMiddleware)


@app.get("/")
async def root():
    return {"message": "API работает! Добро пожаловать на хакатон!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}


app.include_router(hack_router)
app.include_router(team_router)
app.include_router(user_router)
