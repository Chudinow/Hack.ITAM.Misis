from datetime import datetime

from pydantic import BaseModel


class HackSchema(BaseModel):
    id: int
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    tags: str


class HackListSchema(BaseModel):
    hacks: list[HackSchema]
