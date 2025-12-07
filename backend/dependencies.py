# dependencies.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyCookie
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import get_session
from db.models import OrganizerModel
from config import SECRET_KEY

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Для Bearer токенов (если нужны)
security = HTTPBearer()

# Для кук
cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_organizer_cookie(
    request: Request,
    session: AsyncSession = Depends(get_session)
) -> OrganizerModel:
    """
    Получает организатора из куки access_token.
    Также поддерживает Bearer токен в заголовке для совместимости.
    """
    token = None
    
    # 1. Пробуем получить токен из куки
    token = request.cookies.get("access_token")
    
    # 2. Если нет в куках, пробуем из заголовка Authorization (для Swagger)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован. Пожалуйста, войдите в систему."
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        organizer_id = payload.get("sub")
        
        if organizer_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные учетные данные"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен"
        )
    
    result = await session.execute(
        select(OrganizerModel).where(OrganizerModel.id == int(organizer_id))
    )
    organizer = result.scalar_one_or_none()
    
    if organizer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Организатор не найден"
        )
    
    return organizer


async def get_current_organizer_bearer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> OrganizerModel:
    """
    Альтернативная зависимость для Bearer токенов (для Swagger тестирования)
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        organizer_id = payload.get("sub")
        
        if organizer_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    result = await session.execute(
        select(OrganizerModel).where(OrganizerModel.id == int(organizer_id))
    )
    organizer = result.scalar_one_or_none()
    
    if organizer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Organizer not found"
        )
    
    return organizer


def create_error_response(status_code: int, detail: str) -> dict:
    return {
        "detail": detail,
        "status_code": status_code
    }