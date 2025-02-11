import pytest
from app.models.submission import Submission
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_create_submission(client, test_submission_data):
    response = client.post("/submissions/", json=test_submission_data)
    assert response.status_code == 200
    assert response.json()["user_id"] == test_submission_data["user_id"]

def test_create_submission_invalid_data(client):
    response = client.post("/submissions/", json={
        "essay_content": "Test content"
    })
    assert response.status_code == 422
