import pytest
from fastapi import HTTPException
from app.models.content import Content
from sqlmodel import select
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_create_empty_content(test_db, test_user):
    # Test creating an empty content object
    from app.services.content_service import create_empty_content
    content_id = create_empty_content(test_db, test_user.id)
    assert content_id is not None
    
    # Verify the content was created with correct defaults
    content = test_db.exec(select(Content).filter(Content.id == content_id)).first()
    assert content is not None
    assert content.user_id == test_user.id
    assert content.type == "blog_post"

def test_get_content(test_db, test_content):
    # Test getting an existing content
    from app.services.content_service import get
    content = get(test_db, test_content.id)
    assert content.id == test_content.id
    assert content.user_id == test_content.user_id
    assert content.type == test_content.type

def test_get_nonexistent_content(test_db):
    # Test getting a non-existent content
    from app.services.content_service import get
    with pytest.raises(HTTPException) as exc_info:
        get(test_db, 99999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Content not found"

def test_create_content(test_db, test_user):
    # Test creating a new content
    from app.services.content_service import create
    content_id = create(test_db, test_user.id)
    assert content_id is not None
    
    # Verify the content was created with correct defaults
    content = test_db.exec(select(Content).filter(Content.id == content_id)).first()
    assert content is not None
    assert content.user_id == test_user.id
    assert content.type == "blog_post"
