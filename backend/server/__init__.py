from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bot import start_bot
from db import db
from server.mw import ErrorHandlerMiddleware
from server.routes import (
    hack_router,
    org_auth_router,
    org_hacks_router,
    org_public_router,
    org_teams_router,
    team_router,
    user_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio

    asyncio.create_task(start_bot())
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(
    title="pay2win API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://test.xn--80aaaaga5bxbek0bk.xn--p1ai"],
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
app.include_router(org_auth_router)
app.include_router(org_teams_router)
app.include_router(org_public_router)
app.include_router(org_hacks_router)
