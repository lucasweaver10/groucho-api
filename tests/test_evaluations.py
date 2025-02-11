import pytest
from unittest.mock import patch, AsyncMock
from app.services.essay_evaluation_service import EvaluationExistsError
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_create_evaluation(client, test_submission, test_evaluation_data):
    """Test creating an evaluation for a submission"""
    mock_evaluation_result = {
        "id": 1,
        "submission_id": test_submission.id,
        "score": test_evaluation_data["score"],
        "feedback": test_evaluation_data["feedback"],
        "status": "completed"
    }
    
    with patch(
        'app.routers.evaluations.EssayEvaluationService.create_complete_evaluation',
        new_callable=AsyncMock,
        return_value=mock_evaluation_result
    ):
        response = client.post(f"/evaluations/{test_submission.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["submission_id"] == test_submission.id
        assert data["score"] == test_evaluation_data["score"]
        assert data["feedback"] == test_evaluation_data["feedback"]
        assert data["status"] == "completed"

def test_create_evaluation_invalid_submission(client):
    """Test creating an evaluation for a non-existent submission"""
    invalid_submission_id = 99999
    response = client.post(f"/evaluations/{invalid_submission_id}")
    assert response.status_code == 404

def test_create_evaluation_already_exists(client, test_submission, test_evaluation_data):
    """Test creating an evaluation when one already exists"""
    with patch(
        'app.routers.evaluations.EssayEvaluationService.create_complete_evaluation',
        new_callable=AsyncMock,
        side_effect=EvaluationExistsError("Evaluation already exists")
    ):
        response = client.post(f"/evaluations/{test_submission.id}")
        assert response.status_code == 400
        assert response.json()["detail"] == "Evaluation already exists for this submission"