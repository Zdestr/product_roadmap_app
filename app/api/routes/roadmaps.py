from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.api.utils import tags_list_to_string, tags_string_to_list
from app.db.session import get_db
from app.models.roadmap import Roadmap
from app.models.user import User
from app.schemas.roadmap import RoadmapCreate, RoadmapRead, RoadmapUpdate

router = APIRouter(prefix="/roadmaps", tags=["roadmaps"])


@router.get("/", response_model=List[RoadmapRead])
def list_roadmaps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    q: str | None = Query(None, description="Search in title"),
    tag: str | None = Query(None, description="Filter by tag (single)"),
    is_archived: bool | None = Query(None),
):
    query = db.query(Roadmap).filter(Roadmap.owner_id == current_user.id)

    if q:
        like = f"%{q}%"
        query = query.filter(Roadmap.title.ilike(like))

    if tag:
        tag_lower = tag.strip().lower()
        # Простая фильтрация по LIKE
        like = f"%{tag_lower}%"
        query = query.filter(Roadmap.tags.ilike(like))

    if is_archived is not None:
        query = query.filter(Roadmap.is_archived == is_archived)

    roadmaps = query.order_by(Roadmap.created_at.desc()).all()

    # Преобразуем tags к списку для схем
    for rm in roadmaps:
        rm.tags = tags_string_to_list(rm.tags)
    return roadmaps


@router.post("/", response_model=RoadmapRead, status_code=status.HTTP_201_CREATED)
def create_roadmap(
    roadmap_in: RoadmapCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    roadmap = Roadmap(
        title=roadmap_in.title,
        description=roadmap_in.description,
        tags=tags_list_to_string(roadmap_in.tags),
        owner_id=current_user.id,
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    roadmap.tags = tags_string_to_list(roadmap.tags)
    return roadmap


def _get_owned_roadmap_or_404(
    roadmap_id: int,
    db: Session,
    current_user: User,
) -> Roadmap:
    roadmap = (
        db.query(Roadmap)
        .filter(
            Roadmap.id == roadmap_id,
            Roadmap.owner_id == current_user.id,
        )
        .first()
    )
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    return roadmap


@router.get("/{roadmap_id}", response_model=RoadmapRead)
def get_roadmap(
    roadmap_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    roadmap = _get_owned_roadmap_or_404(roadmap_id, db, current_user)
    roadmap.tags = tags_string_to_list(roadmap.tags)
    return roadmap


@router.put("/{roadmap_id}", response_model=RoadmapRead)
def update_roadmap(
    roadmap_id: int,
    roadmap_in: RoadmapUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    roadmap = _get_owned_roadmap_or_404(roadmap_id, db, current_user)

    # Обновляем только заданные поля
    if roadmap_in.title is not None:
        roadmap.title = roadmap_in.title
    if roadmap_in.description is not None:
        roadmap.description = roadmap_in.description
    if roadmap_in.tags is not None:
        roadmap.tags = tags_list_to_string(roadmap_in.tags)
    if roadmap_in.is_archived is not None:
        roadmap.is_archived = roadmap_in.is_archived

    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    roadmap.tags = tags_string_to_list(roadmap.tags)
    return roadmap


@router.delete("/{roadmap_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_roadmap(
    roadmap_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    roadmap = _get_owned_roadmap_or_404(roadmap_id, db, current_user)
    db.delete(roadmap)
    db.commit()
    return None


@router.get("/{roadmap_id}/export")
def export_roadmap(
    roadmap_id: int,
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from fastapi.responses import JSONResponse, PlainTextResponse

    from app.models.milestone import Milestone

    roadmap = _get_owned_roadmap_or_404(roadmap_id, db, current_user)
    roadmap.tags = tags_string_to_list(roadmap.tags)

    milestones = (
        db.query(Milestone)
        .filter(Milestone.roadmap_id == roadmap.id)
        .order_by(Milestone.sort_order)
        .all()
    )

    if format == "json":
        data = {
            "roadmap": {
                "id": roadmap.id,
                "title": roadmap.title,
                "description": roadmap.description,
                "tags": roadmap.tags,
                "created_at": roadmap.created_at.isoformat(),
                "updated_at": roadmap.updated_at.isoformat(),
            },
            "milestones": [
                {
                    "id": m.id,
                    "title": m.title,
                    "description": m.description,
                    "due_at": m.due_at.isoformat(),
                    "status": m.status.value,
                    "sort_order": m.sort_order,
                }
                for m in milestones
            ],
        }
        return JSONResponse(content=data)

    # CSV формат: одна строка на milestone
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "roadmap_id",
            "roadmap_title",
            "milestone_id",
            "milestone_title",
            "due_at",
            "status",
            "sort_order",
        ]
    )
    for m in milestones:
        writer.writerow(
            [
                roadmap.id,
                roadmap.title,
                m.id,
                m.title,
                m.due_at.isoformat(),
                m.status.value,
                m.sort_order,
            ]
        )
    return PlainTextResponse(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="roadmap_{roadmap.id}.csv"'
        },
    )
