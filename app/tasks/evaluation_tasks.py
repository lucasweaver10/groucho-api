from sqlmodel import Session
from ..services.essay_evaluation_service import EssayEvaluationService
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def process_essay_evaluation(message: dict, db: Session):
    """Process an essay evaluation task"""
    submission_id = message['submission_id']
    evaluation_service = EssayEvaluationService(db)
    await evaluation_service.create_complete_evaluation(submission_id)

# Add other task handlers as needed 