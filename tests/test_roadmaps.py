from fastapi import status


def test_create_and_get_roadmap(client, auth_headers):
    resp = client.post(
        "/roadmaps/",
        json={
            "title": "My Roadmap",
            "description": "Test roadmap",
            "tags": ["Python", "Backend"],
        },
        headers=auth_headers,
    )
    assert resp.status_code == status.HTTP_201_CREATED
    roadmap = resp.json()
    assert roadmap["title"] == "My Roadmap"
    assert set(roadmap["tags"]) == {"python", "backend"} or set(
        t.lower() for t in roadmap["tags"]
    ) == {"python", "backend"}

    roadmap_id = roadmap["id"]

    resp = client.get(f"/roadmaps/{roadmap_id}", headers=auth_headers)
    assert resp.status_code == status.HTTP_200_OK
    fetched = resp.json()
    assert fetched["id"] == roadmap_id


def test_list_roadmaps_filter_by_tag(client, auth_headers):
    # создаём два roadmap с разными тегами
    client.post(
        "/roadmaps/",
        json={"title": "RM1", "description": None, "tags": ["tag1"]},
        headers=auth_headers,
    )
    client.post(
        "/roadmaps/",
        json={"title": "RM2", "description": None, "tags": ["tag2"]},
        headers=auth_headers,
    )

    resp = client.get("/roadmaps/?tag=tag1", headers=auth_headers)
    assert resp.status_code == status.HTTP_200_OK
    items = resp.json()
    assert len(items) == 1
    assert items[0]["title"] == "RM1"
