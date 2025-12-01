from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Hack.ITAM.Misis API",
    description="API для хакатона МИСиС",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # На хакатоне разрешаем всем
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API работает! Добро пожаловать на хакатон!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)