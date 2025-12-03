def test_root(client):
    response = client.get("/")
    print(response.json())
    assert response.json().get("a") == "a"
    assert response.status_code == 200

def test_create_user(client):
    response = client.post("/users/", json={"email": "as77jl@gmail.com", "password": "123"})
    print(response.json())
    assert response.json().get("email") == "as77jl@gmail.com"
    assert response.status_code == 201