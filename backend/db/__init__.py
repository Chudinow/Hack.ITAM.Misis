from sqlalchemy.exc import SQLAlchemyError

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USERNAME

from .postgre import Database

db = Database(
    username=DB_USERNAME,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)


async def get_session():
    async with db.session() as session:
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()
