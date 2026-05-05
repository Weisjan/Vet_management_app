from fastapi.testclient import TestClient


def test_register_login_and_me(anonymous_client: TestClient) -> None:
    register_response = anonymous_client.post(
        "/api/v1/auth/register",
        json={
            "email": "User@Example.Test",
            "password": "secure-password",
            "full_name": "Test User",
        },
    )
    assert register_response.status_code == 201
    token = register_response.json()["access_token"]
    assert register_response.json()["user"]["email"] == "user@example.test"

    me_response = anonymous_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.test"

    login_response = anonymous_client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.test", "password": "secure-password"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["token_type"] == "bearer"


def test_protected_endpoint_requires_token(anonymous_client: TestClient) -> None:
    response = anonymous_client.get("/api/v1/clinics")

    assert response.status_code == 401


def test_user_cannot_access_clinic_they_do_not_belong_to(
    anonymous_client: TestClient,
) -> None:
    first_user = anonymous_client.post(
        "/api/v1/auth/register",
        json={
            "email": "first@example.test",
            "password": "secure-password",
            "full_name": "First User",
        },
    ).json()
    first_headers = {"Authorization": f"Bearer {first_user['access_token']}"}
    clinic = anonymous_client.post(
        "/api/v1/clinics",
        json={"name": "Private Clinic"},
        headers=first_headers,
    ).json()

    second_user = anonymous_client.post(
        "/api/v1/auth/register",
        json={
            "email": "second@example.test",
            "password": "secure-password",
            "full_name": "Second User",
        },
    ).json()
    second_headers = {"Authorization": f"Bearer {second_user['access_token']}"}

    response = anonymous_client.get(
        f"/api/v1/clinics/{clinic['id']}",
        headers=second_headers,
    )
    assert response.status_code == 404

    list_response = anonymous_client.get("/api/v1/clinics", headers=second_headers)
    assert list_response.status_code == 200
    assert list_response.json() == []
