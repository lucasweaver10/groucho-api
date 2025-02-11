from fastapi import APIRouter, Request, Depends, BackgroundTasks
from sqlmodel import Session
from ..dependencies import get_db
from ..config import settings  # Import settings to check environment
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TASK_HANDLERS = {
    # 'process_essay_evaluation': process_essay_evaluation,
}

@router.post("")
@router.post("/")
async def handle_lambda_events(request: Request, db: Session = Depends(get_db)):
    """Handle events from AWS Lambda Web Adapter"""
    event = await request.json()
    logger.info(f"Received event: {event}")
    
    # Process SQS events
    if 'Records' in event and event.get('Records')[0].get('eventSource') == 'aws:sqs':
        for record in event['Records']:
            try:
                message = json.loads(record['body'])
                task_name = message.get('task')
                
                if task_name in TASK_HANDLERS:
                    handler = TASK_HANDLERS[task_name]
                    await handler(message, db)
                else:
                    logger.error(f"Unknown task type: {task_name}")
                
            except Exception as e:
                logger.error(f"Error processing task: {str(e)}")
                continue
    
    return {"status": "processed"}

@router.post("/local-process")
async def process_local_events(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Local development endpoint to manually trigger SQS message processing.
    Only available when USE_LOCALSTACK is True.
    """
    if not settings.USE_LOCALSTACK:
        return {"status": "error", "message": "Only available in local development"}

    try:
        # Get messages from LocalStack SQS
        response = settings.sqs_client.receive_message(
            QueueUrl=settings.SQS_QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=1
        )

        messages = response.get('Messages', [])
        for message in messages:
            try:
                body = json.loads(message['Body'])
                task_name = body.get('task')

                if task_name in TASK_HANDLERS:
                    handler = TASK_HANDLERS[task_name]
                    await handler(body, db)
                
                # Delete message after successful processing
                settings.sqs_client.delete_message(
                    QueueUrl=settings.SQS_QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                )
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                continue

        return {
            "status": "success",
            "messages_processed": len(messages)
        }

    except Exception as e:
        logger.error(f"Error in local processing: {str(e)}")
        return {"status": "error", "message": str(e)} 