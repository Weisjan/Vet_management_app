from fastapi.testclient import TestClient

from app.workers.jobs import process_new_mention


def test_create_mention_for_clinic_enqueues_processing_job(client: TestClient) -> None:
    clinic_response = client.post("/api/v1/clinics", json={"name": "Reputation Vet"})
    clinic_id = clinic_response.json()["id"]

    response = client.post(
        f"/api/v1/clinics/{clinic_id}/mentions",
        json={
            "source": " facebook ",
            "source_url": "https://example.test/post/1",
            "content": "The clinic team was kind and helpful.",
            "author_display_name": "Jane D.",
            "published_at": "2026-05-06T10:00:00+00:00",
        },
    )

    assert response.status_code == 201
    mention = response.json()
    assert mention["clinic_id"] == clinic_id
    assert mention["source"] == "facebook"
    assert mention["content"] == "The clinic team was kind and helpful."
    assert mention["author_display_name"] == "Jane D."
    assert mention["status"] == "new"

    enqueued_jobs = client.enqueued_jobs  # type: ignore[attr-defined]
    assert len(enqueued_jobs) == 1
    func, args, kwargs = enqueued_jobs[0]
    assert func is process_new_mention
    assert args == (mention["id"],)
    assert kwargs == {}


def test_list_mentions_is_scoped_to_clinic(client: TestClient) -> None:
    first_clinic = client.post("/api/v1/clinics", json={"name": "First Vet"}).json()
    second_clinic = client.post("/api/v1/clinics", json={"name": "Second Vet"}).json()

    first_mention = client.post(
        f"/api/v1/clinics/{first_clinic['id']}/mentions",
        json={"source": "manual", "content": "First clinic mention"},
    ).json()
    client.post(
        f"/api/v1/clinics/{second_clinic['id']}/mentions",
        json={"source": "manual", "content": "Second clinic mention"},
    )

    response = client.get(f"/api/v1/clinics/{first_clinic['id']}/mentions")

    assert response.status_code == 200
    mentions = response.json()
    assert len(mentions) == 1
    assert mentions[0]["id"] == first_mention["id"]
    assert mentions[0]["clinic_id"] == first_clinic["id"]


def test_create_mention_requires_existing_clinic(client: TestClient) -> None:
    response = client.post(
        "/api/v1/clinics/00000000-0000-0000-0000-000000000000/mentions",
        json={"source": "manual", "content": "Ghost mention"},
    )

    assert response.status_code == 404
