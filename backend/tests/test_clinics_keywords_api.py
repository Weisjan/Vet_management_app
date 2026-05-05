from fastapi.testclient import TestClient


def test_create_list_update_delete_clinic(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/clinics",
        json={
            "name": " Happy Paws ",
            "address": "Main Street 1",
            "phone": "+48123123123",
            "website": "https://example.test",
        },
    )

    assert create_response.status_code == 201
    clinic = create_response.json()
    assert clinic["name"] == "Happy Paws"

    list_response = client.get("/api/v1/clinics")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        f"/api/v1/clinics/{clinic['id']}",
        json={"name": "Happy Paws Clinic"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Happy Paws Clinic"

    delete_response = client.delete(f"/api/v1/clinics/{clinic['id']}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/v1/clinics/{clinic['id']}")
    assert missing_response.status_code == 404


def test_keyword_crud_and_duplicate_validation(client: TestClient) -> None:
    clinic_response = client.post("/api/v1/clinics", json={"name": "Vet House"})
    clinic_id = clinic_response.json()["id"]

    create_response = client.post(
        f"/api/v1/clinics/{clinic_id}/keywords",
        json={"value": " Vet House ", "type": "clinic_name"},
    )
    assert create_response.status_code == 201
    keyword = create_response.json()
    assert keyword["value"] == "Vet House"
    assert keyword["type"] == "clinic_name"
    assert keyword["is_active"] is True

    duplicate_response = client.post(
        f"/api/v1/clinics/{clinic_id}/keywords",
        json={"value": "vet house", "type": "custom"},
    )
    assert duplicate_response.status_code == 409

    list_response = client.get(f"/api/v1/clinics/{clinic_id}/keywords")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        f"/api/v1/keywords/{keyword['id']}",
        json={"value": "Vet House Warsaw", "is_active": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["value"] == "Vet House Warsaw"
    assert update_response.json()["is_active"] is False

    delete_response = client.delete(f"/api/v1/keywords/{keyword['id']}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/v1/keywords/{keyword['id']}")
    assert missing_response.status_code == 404


def test_keyword_requires_existing_clinic(client: TestClient) -> None:
    response = client.post(
        "/api/v1/clinics/00000000-0000-0000-0000-000000000000/keywords",
        json={"value": "ghost clinic"},
    )

    assert response.status_code == 404
