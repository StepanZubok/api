import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.auth import create_access_token
from app import models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} 
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()



@pytest.fixture
def test_user(client):
    user_data = {"email" : "a@gmail.com", "password" : "123"}
    response = client.post("/users/", json = user_data)
    assert response.status_code == 201
    print(response.json())  #{'email': 'a@gmail.com', 'id': 1, 'created_at': '2025-12-04T12:51:44'}
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user

@pytest.fixture
def test_user_2(client):
    user_data = {"email" : "a2@gmail.com", "password" : "123"}
    response = client.post("/users/", json = user_data)
    assert response.status_code == 201
    print(response.json())  #{'email': 'a@gmail.com', 'id': 1, 'created_at': '2025-12-04T12:51:44'}
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})

@pytest.fixture
def authorized_client(client, token):
    # client.headers={**client.headers,"Authorization" : f"Bearer {token}"}
    
    # Set the access_token as a cookie instead of Authorization header
    client.cookies.set("access_token", token)
    return client

@pytest.fixture
def test_posts(test_user, session, test_user_2):     #session bc we will work with dtabase
    posts_data = [{"title": "a", "text" :"B", "account_id":test_user["id"]}, {"title": "b", "text" :"c", "account_id":test_user["id"]}, {"title": "b", "text" :"c", "account_id":test_user_2["id"]}]

    def create_post_model(post):
        return models.PostsTable(**post)
    post_map = map(create_post_model, posts_data)
    posts = list(post_map)

    session.add_all(posts)
    session.commit()
    posts = session.query(models.PostsTable).all()
    return posts

@pytest.fixture
def test_vote(test_posts, test_user, session):
    new_vote = models.Vote(user_id = test_user["id"], post_id =  test_posts[0].id)
    session.add(new_vote)
    session.commit()
    