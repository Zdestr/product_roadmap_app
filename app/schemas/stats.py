from pydantic import BaseModel
from typing import Dict

from app.models.milestone import MilestoneStatus


class StatsResponse(BaseModel):
    total_roadmaps: int
    total_milestones: int
    milestones_by_status: Dict[MilestoneStatus, int]
    overdue_milestones: int
    upcoming_milestones_7d: int

