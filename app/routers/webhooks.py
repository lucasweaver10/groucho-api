from fastapi import APIRouter, Request, HTTPException, Depends
from sqlmodel import Session
from ..database import get_db
from ..services.stripe_service import construct_event, handle_stripe_event
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    # Get the stripe signature from headers
    stripe_signature = request.headers.get("stripe-signature")
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe signature")
    
    # Get the raw request body
    payload = await request.body()
    
    try:
        # Use the stripe service to verify and construct the event
        event = construct_event(payload, stripe_signature)
        
        # Let the stripe service handle the event
        handle_stripe_event(event, db)
        
        logger.info(f"Successfully processed {event['type']} event")
        return {"status": "success"}
    
    except ValueError as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing webhook")