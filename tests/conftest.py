import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.database import get_db
from app.models.user import User
from app.auth import create_access_token
from app.models.content import Content
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
    DATABASE_URL = "postgresql://postgres:postgres@postgres-main:5432/agentgrouchotest"
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
def test_content_data(test_user):
    """Returns submission data without saving to database"""
    return {
        "user_id": test_user.id,
        "type": "blog_post",
        "title": "Test Content Title",
        "description": "Test content description",
        "text": "Test content is here.",        
    }

@pytest.fixture
def test_content(test_db, test_content_data):
    """Creates and returns a test submission in the database"""
    content = Content(**test_content_data)
    test_db.add(content)
    test_db.commit()
    test_db.refresh(content)
    return content

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
        sqs.create_queue(QueueName='agentgroucho-task-queue')
        logger.debug("SQS queue created successfully")
    except Exception as e:
        logger.error(f"Error creating queue: {e}")
        raise
        
    return sqs