from app import schemas
import pytest

def test_get_all_posts(authorized_client, test_posts):
    response = authorized_client.get("/posts/")
    print(response.json(), "all postst")

    def validate(post):
        return schemas.PostVoteResponse(**post)
    posts_list = list(map(validate, response.json()))
    print(posts_list)

    assert len(response.json()) == len(test_posts)
    assert response.status_code == 200
    assert posts_list[0].post.id == test_posts[0].id

def test_unauthorized_user_get_all_posts(client, test_posts):
    response = client.get("/posts/")
    assert response.status_code == 401

def test_unauthorized_user_get_one_post(client, test_posts):
    response = client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401

def test_get_one_post_not_exist(authorized_client, test_posts):
    response = authorized_client.get(f"/posts/11111")
    assert response.status_code == 404

def test_get_one_post(authorized_client, test_posts):
    response = authorized_client.get(f"/posts/{test_posts[0].id}")
    print(response.json())  ##{'post': {'title': 'a', 'text': 'B', 'id': 1, 'created_at': '2025-12-05T11:47:26', 'account_id': 1, 'account': {'id': 1, 'created_at': '2025-12-05T11:47:26'}}, 'vote': 0}
    post  = schemas.PostVoteResponse(**response.json())
    assert post.post.id == test_posts[0].id
    assert post.post.text == test_posts[0].text
    assert response.status_code == 200

@pytest.mark.parametrize("title, text",[
    ("aaa", "bbb0"),
    ("1", "2"),
    ("", ""),
    ("aaa", "bbb0"),
])
def test_create_post(authorized_client, test_user, test_posts, title, text):
    response = authorized_client.post("/posts/", json={"title" : title, "text":text})
    created_post = schemas.PostCreate(**response.json())

    assert created_post.title == title
    assert created_post.text == text
    assert response.status_code == 201

def test_unauthorized_user_create_post(client,test_user, test_posts):
    response = client.post("/posts/", json={"title" : "a-a--aa", "text":"-a-a-a"})
    assert response.status_code == 401


def test_unauthorized_user_delete_post(client, test_user, test_posts):
    response = client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401

def test_user_delete_post(authorized_client, test_user, test_posts):
    response = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 200

def test_user_delete_post_not_exist(authorized_client, test_user, test_posts):
    response = authorized_client.delete("/posts/1111")
    assert response.status_code == 404


def test_user_delete_post_not_his(authorized_client, test_user, test_posts):
    response = authorized_client.delete(f"/posts/{test_posts[2].id}")
    assert response.status_code == 403
    

def test_update_post(authorized_client, test_user, test_posts):
    data = {"title":"0", "text":"0"}
    response = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
    updated_post = schemas.PostUpdate(**response.json())

    assert updated_post.title == data["title"]
    assert updated_post.text == data["text"]
    assert response.status_code == 200

def test_update_other_user_post(authorized_client, test_user, test_user_2, test_posts):
    data = {"title":"0", "text":"0"}
    response = authorized_client.put(f"/posts/{test_posts[2].id}", json=data)
    assert response.status_code == 403

def test_unauthorized_user_update_post(client, test_user, test_user_2, test_posts):
    data = {"title":"0", "text":"0"}
    response = client.put(f"/posts/{test_posts[0].id}", json=data)
    assert response.status_code == 401

def test_user_update_post_not_exist(authorized_client, test_user, test_posts):
    data = {"title":"0", "text":"0"}
    response = authorized_client.put("/posts/1111", json=data)
    assert response.status_code == 404