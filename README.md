# Hack.ITAM.Misis

Платформа для управления хакатонами: организаторы создают мероприятия, участники регистрируются, формируют команды, а организаторы управляют процессом. Проект разработан в рамках хакатона **Hack.ITAM** командой из 3 человек.

## Технологический стек

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy (async), Pydantic, JWT, PostgreSQL
- **Frontend**: React, TypeScript, CSS
- **Инфраструктура**: Docker, docker-compose

## Структура проекта

- `backend/` – серверная часть на FastAPI.
- `frontend/` – клиентская часть на React.
- `docker-compose.yml` – конфигурация для запуска всех сервисов.

## Вклад участников

- **Николай Чудинов** – разработка всего backend‑модуля для организатора (`backend/server/routes/org`):
  - Аутентификация организаторов (JWT в httpOnly cookies, регистрация, вход, выход).
  - CRUD хакатонов с валидацией дат и размеров команд, загрузкой/удалением фотографий.
  - Управление командами и участниками (списки с фильтрацией, ручное распределение участников по командам, одобрение/отклонение команд).
  - Аналитика (количество команд/участников, заполненность, распределение по ролям, оставшиеся места) и экспорт в CSV.
  - Публичное API (без авторизации) для получения списка хакатонов, команд и участников (интеграция с Telegram‑ботом).

- **** – разработка фронтенда на React (папка `frontend/`).

- **fL1pSt3r** – настройка Docker, PostgreSQL, помощь в интеграции бэкенда и фронтенда.

- **MorS1337** –

## Запуск проекта

### Локально

**Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate   # или venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # заполните переменные окружения
uvicorn server.main:app --reload --port 8000

**Frontend**

```bash
cd frontend
npm install
npm start
Через Docker
bash
docker-compose up --build
Документация API (Swagger) после запуска доступна по адресу: http://localhost:8000/docs
