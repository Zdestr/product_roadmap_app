from datetime import datetime, date
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class MilestoneStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(255), nullable=False, index=True)
    description = Column(String, nullable=True)

    due_at = Column(Date, nullable=False)
    status = Column(
        Enum(MilestoneStatus, name="milestone_status"),
        default=MilestoneStatus.PLANNED,
        nullable=False,
    )

    sort_order = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    roadmap = relationship("Roadmap", back_populates="milestones")
