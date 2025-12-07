from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.milestone import Milestone, MilestoneStatus
from app.models.roadmap import Roadmap
from app.models.user import User
from app.schemas.milestone import MilestoneCreate, MilestoneRead, MilestoneUpdate

router = APIRouter(prefix="/milestones", tags=["milestones"])


def _ensure_roadmap_owned(
    roadmap_id: int,
    db: Session,
    current_user: User,
) -> Roadmap:
    roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.id == roadmap_id, Roadmap.owner_id == current_user.id)
        .first()
    )
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    return roadmap


def _get_owned_milestone_or_404(
    milestone_id: int,
    db: Session,
    current_user: User,
) -> Milestone:
    # join с Roadmap для проверки владельца
    milestone = (
        db.query(Milestone)
        .join(Roadmap, Milestone.roadmap_id == Roadmap.id)
        .filter(
            Milestone.id == milestone_id,
            Roadmap.owner_id == current_user.id,
        )
        .first()
    )
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return milestone


@router.get("/", response_model=List[MilestoneRead])
def list_milestones(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    status_filter: MilestoneStatus | None = Query(None, alias="status"),
    due_before: date | None = Query(None),
    due_after: date | None = Query(None),
    roadmap_id: int | None = Query(None),
):
    query = (
        db.query(Milestone)
        .join(Roadmap, Milestone.roadmap_id == Roadmap.id)
        .filter(Roadmap.owner_id == current_user.id)
    )

    if status_filter is not None:
        query = query.filter(Milestone.status == status_filter)
    if due_before is not None:
        query = query.filter(Milestone.due_at <= due_before)
    if due_after is not None:
        query = query.filter(Milestone.due_at >= due_after)
    if roadmap_id is not None:
        query = query.filter(Milestone.roadmap_id == roadmap_id)

    milestones = query.order_by(Milestone.due_at).all()
    return milestones


@router.post("/", response_model=MilestoneRead, status_code=status.HTTP_201_CREATED)
def create_milestone(
    milestone_in: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    roadmap = _ensure_roadmap_owned(milestone_in.roadmap_id, db, current_user)

    # Дополнительная валидация: дедлайн не раньше даты создания roadmap
    if milestone_in.due_at < roadmap.created_at.date():
        raise HTTPException(
            status_code=400,
            detail="Milestone due_at cannot be earlier than roadmap creation date",
        )

    milestone = Milestone(
        title=milestone_in.title,
        description=milestone_in.description,
        due_at=milestone_in.due_at,
        status=milestone_in.status,
        sort_order=milestone_in.sort_order,
        roadmap_id=milestone_in.roadmap_id,
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


@router.get("/{milestone_id}", response_model=MilestoneRead)
def get_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    milestone = _get_owned_milestone_or_404(milestone_id, db, current_user)
    return milestone


@router.put("/{milestone_id}", response_model=MilestoneRead)
def update_milestone(
    milestone_id: int,
    milestone_in: MilestoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    milestone = _get_owned_milestone_or_404(milestone_id, db, current_user)

    if milestone_in.title is not None:
        milestone.title = milestone_in.title
    if milestone_in.description is not None:
        milestone.description = milestone_in.description
    if milestone_in.due_at is not None:
        # Повторная валидация (могут двигать в прошлое или до создания roadmap)
        roadmap = db.query(Roadmap).filter(Roadmap.id == milestone.roadmap_id).first()
        if milestone_in.due_at < roadmap.created_at.date():
            raise HTTPException(
                status_code=400,
                detail="Milestone due_at cannot be earlier than roadmap creation date",
            )
        if milestone_in.due_at < date.today():
            raise HTTPException(
                status_code=400,
                detail="Milestone due_at cannot be in the past",
            )
        milestone.due_at = milestone_in.due_at
    if milestone_in.status is not None:
        milestone.status = milestone_in.status
    if milestone_in.sort_order is not None:
        milestone.sort_order = milestone_in.sort_order

    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


@router.delete("/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    milestone = _get_owned_milestone_or_404(milestone_id, db, current_user)
    db.delete(milestone)
    db.commit()
    return None
