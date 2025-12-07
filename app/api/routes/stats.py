from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.milestone import Milestone, MilestoneStatus
from app.models.roadmap import Roadmap
from app.models.user import User
from app.schemas.stats import StatsResponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/", response_model=StatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Всего roadmaps
    total_roadmaps = (
        db.query(func.count(Roadmap.id))
        .filter(Roadmap.owner_id == current_user.id)
        .scalar()
    )

    # Всего milestones
    total_milestones = (
        db.query(func.count(Milestone.id))
        .join(Roadmap, Milestone.roadmap_id == Roadmap.id)
        .filter(Roadmap.owner_id == current_user.id)
        .scalar()
    )

    # По статусам
    rows = (
        db.query(Milestone.status, func.count(Milestone.id))
        .join(Roadmap, Milestone.roadmap_id == Roadmap.id)
        .filter(Roadmap.owner_id == current_user.id)
        .group_by(Milestone.status)
        .all()
    )

    milestones_by_status: dict[MilestoneStatus, int] = {
        status: 0 for status in MilestoneStatus
    }
    for status, cnt in rows:
        milestones_by_status[status] = cnt

    today = date.today()
    upcoming_limit = today + timedelta(days=7)

    # Просроченные
    overdue_milestones = (
        db.query(func.count(Milestone.id))
        .join(Roadmap, Milestone.roadmap_id == Roadmap.id)
        .filter(
            Roadmap.owner_id == current_user.id,
            Milestone.due_at < today,
            Milestone.status != MilestoneStatus.DONE,
        )
        .scalar()
    )

    # Ближайшие 7 дней
    upcoming_milestones_7d = (
        db.query(func.count(Milestone.id))
        .join(Roadmap, Milestone.roadmap_id == Roadmap.id)
        .filter(
            Roadmap.owner_id == current_user.id,
            Milestone.due_at >= today,
            Milestone.due_at <= upcoming_limit,
            Milestone.status.in_(
                [MilestoneStatus.PLANNED, MilestoneStatus.IN_PROGRESS]
            ),
        )
        .scalar()
    )

    return StatsResponse(
        total_roadmaps=total_roadmaps,
        total_milestones=total_milestones,
        milestones_by_status=milestones_by_status,
        overdue_milestones=overdue_milestones,
        upcoming_milestones_7d=upcoming_milestones_7d,
    )
