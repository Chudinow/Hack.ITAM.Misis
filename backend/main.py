import asyncio

import uvicorn

from bot import start_bot
from server import app

if __name__ == "__main__":
    asyncio.run(start_bot())

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
