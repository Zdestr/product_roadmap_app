from datetime import date, timedelta

from fastapi import status


def test_stats_empty(client, auth_headers):
    resp = client.get("/stats/", headers=auth_headers)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["total_roadmaps"] == 0
    assert data["total_milestones"] == 0
    assert data["overdue_milestones"] == 0
    assert data["upcoming_milestones_7d"] == 0


def test_stats_with_data(client, auth_headers, db_session, test_user):
    # Создаём один roadmap через API
    rm_resp = client.post(
        "/roadmaps/",
        json={"title": "RM", "description": None, "tags": []},
        headers=auth_headers,
    )
    assert rm_resp.status_code == status.HTTP_201_CREATED
    roadmap_id = rm_resp.json()["id"]

    today = date.today()
    overdue = today - timedelta(days=1)
    upcoming = today + timedelta(days=3)

    # 1 overdue milestone: создаём НАПРЯМУЮ В БД, обходя API (который не пускает due_at в прошлом)
    from app.models.milestone import Milestone, MilestoneStatus

    overdue_ms = Milestone(
        title="Overdue",
        description="",
        due_at=overdue,
        status=MilestoneStatus.PLANNED,
        sort_order=1,
        roadmap_id=roadmap_id,
    )
    db_session.add(overdue_ms)
    db_session.commit()

    # 1 upcoming milestone создаём через API (API разрешает будущие даты)
    resp = client.post(
        "/milestones/",
        json={
            "title": "Upcoming",
            "description": "",
            "due_at": upcoming.isoformat(),
            "status": "in_progress",
            "sort_order": 2,
            "roadmap_id": roadmap_id,
        },
        headers=auth_headers,
    )
    assert resp.status_code == status.HTTP_201_CREATED

    # Проверяем статистику
    resp = client.get("/stats/", headers=auth_headers)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()

    assert data["total_roadmaps"] == 1
    assert data["total_milestones"] == 2
    assert data["overdue_milestones"] == 1
    assert data["upcoming_milestones_7d"] == 1
