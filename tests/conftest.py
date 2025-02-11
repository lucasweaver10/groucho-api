import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.database import get_db
from app.models.user import User
from app.auth import create_access_token
from app.models.submission import Submission
from app.models.post import Post
import time
import boto3
from botocore.exceptions import ClientError
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Simple test DB setup
@pytest.fixture
def test_db():
    DATABASE_URL = "postgresql://postgres:postgres@postgres-main:5432/essay-checker-test"
    engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        logger.debug("Creating new test database session")
        yield session
        
    SQLModel.metadata.drop_all(engine)

# Basic test user
@pytest.fixture
def test_user(test_db):
    user = User(email="test@example.com")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

# Test client with DB override
@pytest.fixture
def client(test_db):
    """Test client with DB override"""
    def get_test_db():
        return test_db
    
    # Set the override before creating the client
    app.dependency_overrides[get_db] = get_test_db
    
    with TestClient(app) as client:
        yield client
        
    # Clear the override after
    app.dependency_overrides.clear()

# Auth token
@pytest.fixture
def test_token(test_user):
    return create_access_token(user_id=test_user.id)

# Authorized client
@pytest.fixture
def authorized_client(client, test_token):
    client.headers["Authorization"] = f"Bearer {test_token}"
    return client

@pytest.fixture
def test_submission_data(test_user):
    """Returns submission data without saving to database"""
    return {
        "user_id": test_user.id,
        "exam_type": "IELTS",
        "exam_name": "Academic",
        "essay_task": "Writing Task 2",
        "essay_topic": "Test Topic",
        "essay_content": "Test content",
        "word_count": 250,
        "ai_evaluation": True,
        "human_evaluation": False,
        "status": "submitted"
    }

@pytest.fixture
def test_submission(test_db, test_submission_data):
    """Creates and returns a test submission in the database"""
    submission = Submission(**test_submission_data)
    test_db.add(submission)
    test_db.commit()
    test_db.refresh(submission)
    return submission

@pytest.fixture(scope="session", autouse=True)
def ensure_localstack_ready():
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            sqs = boto3.client(
                'sqs',
                endpoint_url='http://localstack:4566',
                region_name='us-west-2',
                aws_access_key_id='test',
                aws_secret_access_key='test'
            )
            sqs.list_queues()
            return
        except ClientError:
            time.sleep(1)
    raise Exception("LocalStack failed to start")

@pytest.fixture(scope="session", autouse=True)
def setup_sqs_queue(ensure_localstack_ready):
    sqs = boto3.client(
        'sqs',
        endpoint_url='http://localstack:4566',
        region_name='us-west-2',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )
    
    try:
        sqs.create_queue(QueueName='essay-evaluation-queue')
        logger.debug("SQS queue created successfully")
    except Exception as e:
        logger.error(f"Error creating queue: {e}")
        raise
        
    return sqs

@pytest.fixture
def test_evaluation_data(test_submission):
    return {
        "submission_id": test_submission.id,
        "score": 7.5,
        "feedback": "Good essay"
    }

@pytest.fixture
def test_post_data():
    """Returns post data without saving to database"""
    return {
        "site_id": 1,
        "title": "Test Post",
        "content": "This is test content",
        "status": "published",
        "type": "post",
        "author_id": 1,
        "user_id": 1,
        "slug": "test-post",
        "excerpt": "Test excerpt",
        "meta_description": "Test meta description",
        "featured_image_url": "https://example.com/image.jpg",
        "published_date": datetime.utcnow(),
        "published_date_gmt": datetime.utcnow()
    }

@pytest.fixture
def test_post(test_db, test_post_data):
    """Creates and returns a test post in the database"""
    post = Post(**test_post_data)
    test_db.add(post)
    test_db.commit()
    test_db.refresh(post)
    return post