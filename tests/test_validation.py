from datetime import date, timedelta

from fastapi import status


def _create_roadmap(client, auth_headers):
    resp = client.post(
        "/roadmaps/",
        json={"title": "RM", "description": None, "tags": []},
        headers=auth_headers,
    )
    assert resp.status_code == status.HTTP_201_CREATED
    return resp.json()["id"]


def test_milestone_cannot_be_in_past(client, auth_headers):
    roadmap_id = _create_roadmap(client, auth_headers)
    past = date.today() - timedelta(days=1)

    resp = client.post(
        "/milestones/",
        json={
            "title": "Past",
            "description": "",
            "due_at": past.isoformat(),
            "status": "planned",
            "sort_order": 1,
            "roadmap_id": roadmap_id,
        },
        headers=auth_headers,
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_owner_only_access(client, db_session, test_user):
    from app.core.security import get_password_hash, create_access_token
    from app.models.user import User
    from app.models.roadmap import Roadmap

    other_user = User(
        email="other@example.com",
        full_name="Other",
        hashed_password=get_password_hash("otherpass"),
        is_active=True,
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)

    rm = Roadmap(
        title="Private RM",
        description=None,
        tags=None,
        owner_id=test_user.id,
    )
    db_session.add(rm)
    db_session.commit()
    db_session.refresh(rm)

    token = create_access_token(subject=other_user.id)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get(f"/roadmaps/{rm.id}", headers=headers)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
