from datetime import date, timedelta

from fastapi import status


def create_roadmap(client, auth_headers):
    resp = client.post(
        "/roadmaps/",
        json={"title": "RM", "description": None, "tags": []},
        headers=auth_headers,
    )
    assert resp.status_code == status.HTTP_201_CREATED
    return resp.json()["id"]


def test_create_milestone_success(client, auth_headers):
    roadmap_id = create_roadmap(client, auth_headers)
    due = date.today() + timedelta(days=3)

    resp = client.post(
        "/milestones/",
        json={
            "title": "MS1",
            "description": "desc",
            "due_at": due.isoformat(),
            "status": "planned",
            "sort_order": 1,
            "roadmap_id": roadmap_id,
        },
        headers=auth_headers,
    )
    assert resp.status_code == status.HTTP_201_CREATED
    ms = resp.json()
    assert ms["title"] == "MS1"
    assert ms["due_at"] == due.isoformat()


def test_create_milestone_due_in_past_fails(client, auth_headers):
    roadmap_id = create_roadmap(client, auth_headers)
    past = date.today() - timedelta(days=1)

    resp = client.post(
        "/milestones/",
        json={
            "title": "MS Past",
            "description": "",
            "due_at": past.isoformat(),
            "status": "planned",
            "sort_order": 1,
            "roadmap_id": roadmap_id,
        },
        headers=auth_headers,
    )
    assert (
        resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    )  # сработала pydantic-валидация
