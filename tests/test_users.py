from fastapi.testclient import TestClient


def test_create_user_success(client: TestClient) -> None:
    """Test creating a valid user."""
    payload = {
        "email": "alice@example.com",
        "username": "alice",
        "full_name": "Alice Smith",
        "is_active": True,
    }
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["email"] == "alice@example.com"
    assert data["username"] == "alice"
    assert data["full_name"] == "Alice Smith"
    assert data["is_active"] is True
    assert "created_at" in data
    assert "updated_at" in data


def test_create_user_validation_error(client: TestClient) -> None:
    """Test user creation fails when invalid payload is supplied."""
    payload = {
        "email": "not-an-email",
        "username": "a",  # too short (min length 3)
    }
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "ValidationError"


def test_create_user_duplicate_email(client: TestClient) -> None:
    """Test creating a user with an already registered email."""
    payload = {
        "email": "duplicate@example.com",
        "username": "user1",
    }
    res1 = client.post("/api/v1/users", json=payload)
    assert res1.status_code == 201

    payload2 = {
        "email": "duplicate@example.com",
        "username": "user2",
    }
    res2 = client.post("/api/v1/users", json=payload2)
    assert res2.status_code == 409
    data = res2.json()
    assert data["error"] == "UserAlreadyExistsError"
    assert "email" in data["detail"]


def test_create_user_duplicate_username(client: TestClient) -> None:
    """Test creating a user with an already registered username."""
    payload1 = {
        "email": "user1@example.com",
        "username": "samename",
    }
    res1 = client.post("/api/v1/users", json=payload1)
    assert res1.status_code == 201

    payload2 = {
        "email": "user2@example.com",
        "username": "samename",
    }
    res2 = client.post("/api/v1/users", json=payload2)
    assert res2.status_code == 409
    data = res2.json()
    assert data["error"] == "UserAlreadyExistsError"
    assert "username" in data["detail"]


def test_get_user_by_id_success(client: TestClient) -> None:
    """Test retrieving an existing user by ID."""
    create_res = client.post(
        "/api/v1/users",
        json={"email": "bob@example.com", "username": "bobby", "full_name": "Bob Jones"},
    )
    user_id = create_res.json()["id"]

    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "bobby"


def test_get_user_by_id_not_found(client: TestClient) -> None:
    """Test retrieving a non-existent user returns 404."""
    response = client.get("/api/v1/users/99999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "UserNotFoundError"


def test_list_users_pagination(client: TestClient) -> None:
    """Test listing users with pagination."""
    # Seed 3 users
    for i in range(1, 4):
        client.post(
            "/api/v1/users",
            json={"email": f"user{i}@example.com", "username": f"user{i}"},
        )

    # First page: limit 2
    res = client.get("/api/v1/users?skip=0&limit=2")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["skip"] == 0
    assert data["limit"] == 2

    # Second page: skip 2, limit 2
    res2 = client.get("/api/v1/users?skip=2&limit=2")
    assert res2.status_code == 200
    data2 = res2.json()
    assert len(data2["items"]) == 1
    assert data2["items"][0]["username"] == "user3"


def test_update_user_success(client: TestClient) -> None:
    """Test updating user fields successfully."""
    create_res = client.post(
        "/api/v1/users",
        json={"email": "charlie@example.com", "username": "charlie", "full_name": "Charlie"},
    )
    user_id = create_res.json()["id"]

    update_payload = {"full_name": "Charlie Chaplin", "is_active": False}
    response = client.put(f"/api/v1/users/{user_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Charlie Chaplin"
    assert data["is_active"] is False
    assert data["username"] == "charlie"


def test_update_user_not_found(client: TestClient) -> None:
    """Test updating a non-existent user returns 404."""
    response = client.put("/api/v1/users/99999", json={"full_name": "Ghost"})
    assert response.status_code == 404
    assert response.json()["error"] == "UserNotFoundError"


def test_update_user_conflict(client: TestClient) -> None:
    """Test updating a user to an existing email or username causes 409 conflict."""
    client.post("/api/v1/users", json={"email": "first@example.com", "username": "first"})
    res2 = client.post("/api/v1/users", json={"email": "second@example.com", "username": "second"})
    user2_id = res2.json()["id"]

    # Attempt to update user2's email to user1's email
    conflict_res = client.put(f"/api/v1/users/{user2_id}", json={"email": "first@example.com"})
    assert conflict_res.status_code == 409
    assert conflict_res.json()["error"] == "UserAlreadyExistsError"


def test_delete_user_success(client: TestClient) -> None:
    """Test deleting an existing user."""
    create_res = client.post(
        "/api/v1/users",
        json={"email": "david@example.com", "username": "david"},
    )
    user_id = create_res.json()["id"]

    delete_res = client.delete(f"/api/v1/users/{user_id}")
    assert delete_res.status_code == 204

    # Verify user is gone
    get_res = client.get(f"/api/v1/users/{user_id}")
    assert get_res.status_code == 404


def test_delete_user_not_found(client: TestClient) -> None:
    """Test deleting a non-existent user returns 404."""
    response = client.delete("/api/v1/users/99999")
    assert response.status_code == 404
    assert response.json()["error"] == "UserNotFoundError"

