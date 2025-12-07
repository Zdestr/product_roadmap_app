from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, constr, validator

from app.models.milestone import MilestoneStatus


class MilestoneBase(BaseModel):
    title: constr(strip_whitespace=True, min_length=1, max_length=255)
    description: Optional[str] = None
    due_at: date
    status: MilestoneStatus = MilestoneStatus.PLANNED
    sort_order: int = 0

    @validator("due_at")
    def validate_due_at_not_in_past(cls, v: date) -> date:
        today = date.today()
        if v < today:
            raise ValueError("due_at cannot be in the past")
        return v


class MilestoneCreate(MilestoneBase):
    roadmap_id: int


class MilestoneUpdate(BaseModel):
    title: constr(strip_whitespace=True, min_length=1, max_length=255) | None = None
    description: str | None = None
    due_at: date | None = None
    status: MilestoneStatus | None = None
    sort_order: int | None = None


class MilestoneRead(MilestoneBase):
    id: int
    roadmap_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
