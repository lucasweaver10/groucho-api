import pytest
from app.models.post import Post
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def multiple_posts(test_db, test_post_data):
    """Creates multiple test posts with incremental data"""
    posts = [
        Post(
            **{
                **test_post_data,
                "title": f"Test Post {i}",
                "content": f"This is test content {i}",
                "slug": f"test-post-{i}",
                "excerpt": f"Test excerpt {i}",
                "meta_description": f"Test meta description {i}",
                "featured_image_url": f"https://example.com/image-{i}.jpg",
            }
        )
        for i in range(3)
    ]
    for post in posts:
        test_db.add(post)
    test_db.commit()
    for post in posts:
        test_db.refresh(post)
    return posts

def test_get_posts_by_site(client, multiple_posts):
    """Test getting all posts for a specific site"""
    response = client.get("/posts/1")
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == 3
    assert all(post["site_id"] == 1 for post in posts)

def test_get_posts_by_site_empty(client):
    """Test getting posts for a site with no posts"""
    response = client.get("/posts/999")
    assert response.status_code == 200
    assert response.json() == []

def test_get_post_by_slug(client, test_post):
    """Test getting a specific post by site_id and slug"""
    response = client.get(f"/posts/1/test-post")
    assert response.status_code == 200
    post = response.json()
    assert post["slug"] == "test-post"
    assert post["site_id"] == 1
    assert post["title"] == "Test Post"

def test_get_post_by_slug_not_found(client):
    """Test getting a non-existent post"""
    response = client.get("/posts/1/non-existent-post")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

def test_get_post_by_slug_wrong_site(client, test_post):
    """Test getting a post with correct slug but wrong site_id"""
    response = client.get("/posts/999/test-post")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"
