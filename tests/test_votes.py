def test_vote_post(authorized_client, test_posts):
    response = authorized_client.post("/votes/", json={"post_id":test_posts[0].id, "vote_option":1})
    assert response.status_code == 201

def test_vote_post_twice(authorized_client, test_posts, test_vote):
    response = authorized_client.post("/votes/", json={"post_id":test_posts[0].id, "vote_option":1})
    assert response.status_code == 409


def test_delete_vote_post(authorized_client, test_posts, test_vote):
    response = authorized_client.post("/votes/", json={"post_id":test_posts[0].id, "vote_option":0})
    assert response.status_code == 201

def test_delete_vote_that_not_exist(authorized_client, test_posts):     #no test_vote bc i dont want this func to run test_vote fixture to create post ; no post - > try delete post that doesnt exist - > error 
    response = authorized_client.post("/votes/", json={"post_id":test_posts[0].id, "vote_option":0})
    assert response.status_code == 404

def test_vote_post_that_not_exist(authorized_client, test_posts, test_vote):    
    response = authorized_client.post("/votes/", json={"post_id":11111, "vote_option":1})
    assert response.status_code == 404


def test_vote_post_unauthorized_user(client, test_posts):    
    response = client.post("/votes/", json={"post_id":test_posts[0].id, "vote_option":1})
    assert response.status_code == 401