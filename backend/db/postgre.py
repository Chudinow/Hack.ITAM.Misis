from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class Database:
    def __init__(
        self, username: str, password: str, host: str, port: int, database: str
    ):
        self.url = URL.create(
            drivername="postgresql+asyncpg",
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
        )
        self.engine: AsyncEngine | None = None
        self.session: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        self.engine: AsyncEngine = create_async_engine(
            self.url,
            echo=False,
        )
        self.session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def disconnect(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()
