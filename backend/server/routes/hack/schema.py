from datetime import datetime

from pydantic import BaseModel


class HackSchema(BaseModel):
    id: int
    name: str
    description: str
    photo_url: str | None
    start_date: datetime
    end_date: datetime
    tags: str


class MetaSchema(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int


class HackListSchema(BaseModel):
    hacks: list[HackSchema]
    meta: MetaSchema
