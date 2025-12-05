import hashlib
import hmac
import time


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
