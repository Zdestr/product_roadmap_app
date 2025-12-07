from datetime import datetime
from typing import List

from pydantic import BaseModel, constr


class RoadmapBase(BaseModel):
    title: constr(strip_whitespace=True, min_length=1, max_length=255)
    description: str | None = None
    tags: List[constr(strip_whitespace=True, min_length=1, max_length=50)] = []


class RoadmapCreate(RoadmapBase):
    pass


class RoadmapUpdate(BaseModel):
    title: constr(strip_whitespace=True, min_length=1, max_length=255) | None = None
    description: str | None = None
    tags: list[str] | None = None
    is_archived: bool | None = None


class RoadmapRead(RoadmapBase):
    id: int
    owner_id: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
