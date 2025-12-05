import pytest
from app import schemas
from jose import jwt
from app.config import settings

def test_root(client):
    response = client.get("/")
    print(response.json())
    assert response.json().get("a") == "a"
    assert response.status_code == 200

def test_create_user(client):
    response = client.post("/users/", json={"email": "a@gmail.com", "password": "123"})
    new_user = schemas.UserResponse(**response.json())
    assert new_user.email == "a@gmail.com"
    assert response.status_code == 201

def test_login_user(client, test_user):
    response = client.post("/login", data={"username": test_user["email"], "password": test_user["password"]})    #data bc in postman we use form-data, not json
    loggedin_user = schemas.Token(**response.json())
    payload = jwt.decode(loggedin_user.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    id = payload.get("user_id")
    assert id == test_user["id"]
    # assert loggedin_user.token_type == "bearer"
    assert loggedin_user.token_type == None # test if default none value is set
    assert response.status_code == 200

@pytest.mark.parametrize("email, password, status_code",[
    ("A@gmail.com", "123", 403),
    (None, "123", 403),
    ("a", None, 403),
    (None, None, 403)
])
def test_incorrect_login_user(client, test_user, email, password, status_code):
    response = client.post("/login", data={"username":email, "password": password})   
    assert response.status_code == status_code
    # assert response.json().get(""detail) == "Invalid Credentials"


