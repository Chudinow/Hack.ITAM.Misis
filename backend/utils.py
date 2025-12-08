import hashlib
import hmac
import time

import jwt
from fastapi import HTTPException, Request

from config import SECRET_KEY


def verify_telegram_auth(payload: dict, bot_token: str) -> bool:
    data = payload.copy()
    received_hash = data.pop("hash", None)
    if not received_hash:
        return False

    data_check_arr = []
    for k in sorted(data.keys()):
        v = data[k]
        if v is None:
            continue
        data_check_arr.append(f"{k}={v}")
    data_check_string = "\n".join(data_check_arr)

    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    # Проверка времени, не старше 1 дня
    try:
        auth_date = int(payload.get("auth_date", 0))
    except Exception:
        return False
    if abs(time.time() - auth_date) > 86400:
        return False

    return hmac.compare_digest(hmac_hash, received_hash)


def get_current_user_id(request: Request) -> int:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing access_token cookie")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="user_id not found")

    return user_id
