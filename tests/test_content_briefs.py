import pytest
from fastapi import HTTPException
from sqlmodel import select
from app.models.content_brief import ContentBrief
from app.models.content import Content
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def test_content_brief_data(test_user):
    """Returns content brief data without saving to database"""
    return {
        "user_id": test_user.id,
        "title": "Test Brief Title",
        "description": "Test brief description",
        "custom_data": {"key": "value"},
    }

@pytest.fixture
def test_content_brief(test_db, test_content_brief_data, test_content):
    """Creates and returns a test content brief in the database"""
    content_brief = ContentBrief(
        **test_content_brief_data,
        content_id=test_content.id
    )
    test_db.add(content_brief)
    test_db.commit()
    test_db.refresh(content_brief)
    return content_brief

def test_create_content_brief(test_db, test_content_brief_data):
    # Test creating a new content brief
    from app.services.content_brief_service import create
    
    # Create content brief without content_id (should create new content)
    content_brief = ContentBrief(**test_content_brief_data)
    result = create(test_db, content_brief)
    
    # Verify the content brief was created
    assert result.id is not None
    assert result.user_id == test_content_brief_data["user_id"]
    assert result.title == test_content_brief_data["title"]
    assert result.description == test_content_brief_data["description"]
    assert result.custom_data == test_content_brief_data["custom_data"]
    
    # Verify a new content was created and linked
    assert result.content_id is not None
    content = test_db.exec(select(Content).where(Content.id == result.content_id)).first()
    assert content is not None
    assert content.user_id == test_content_brief_data["user_id"]

def test_create_content_brief_with_existing_content(test_db, test_content_brief_data, test_content):
    # Test creating a content brief with existing content
    from app.services.content_brief_service import create
    
    # Create content brief with existing content_id
    content_brief = ContentBrief(
        **test_content_brief_data,
        content_id=test_content.id
    )
    result = create(test_db, content_brief)
    
    # Verify the content brief was created with the existing content
    assert result.content_id == test_content.id

def test_get_content_brief(test_db, test_content_brief):
    # Test getting an existing content brief
    from app.services.content_brief_service import get_content_brief_by_id
    
    brief = get_content_brief_by_id(db=test_db, content_brief_id=test_content_brief.id)
    assert brief.id == test_content_brief.id
    assert brief.user_id == test_content_brief.user_id
    assert brief.title == test_content_brief.title
    assert brief.description == test_content_brief.description
    assert brief.content_id == test_content_brief.content_id

def test_get_nonexistent_content_brief(test_db):
    # Test getting a non-existent content brief
    from app.services.content_brief_service import get_content_brief_by_id
    
    with pytest.raises(HTTPException) as exc_info:
        get_content_brief_by_id(db=test_db, content_brief_id=99999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Content brief not found"

def test_get_or_create_content_id(test_db, test_user, test_content):
    # Test the get_or_create_content_id function
    from app.services.content_brief_service import get_or_create_content_id
    
    # Test with existing content_id
    brief_with_content = ContentBrief(user_id=test_user.id, content_id=test_content.id)
    content_id = get_or_create_content_id(test_db, brief_with_content, test_user.id)
    assert content_id == test_content.id
    
    # Test without content_id (should create new)
    brief_without_content = ContentBrief(user_id=test_user.id)
    new_content_id = get_or_create_content_id(test_db, brief_without_content, test_user.id)
    assert new_content_id is not None
    assert new_content_id != test_content.id
    
    # Verify new content was created
    new_content = test_db.exec(select(Content).where(Content.id == new_content_id)).first()
    assert new_content is not None
    assert new_content.user_id == test_user.id