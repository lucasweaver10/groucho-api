from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserMeResponse
from app.auth import (
    create_access_token, 
    get_current_user, 
    create_magic_token, 
    send_magic_link, 
    get_current_user_from_magic_link,
    SECRET_KEY,
    ALGORITHM
)
from app.schemas.token import Token
import logging
import os
from jose import jwt, JWTError

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register")
async def register_user(
    request: Request,
    user: UserCreate, 
    db: Session = Depends(get_db)
):
    # Log the request details
    body = await request.json()
    logger.info(f"Register request received - Headers: {dict(request.headers)}")
    logger.info(f"Register request body: {body}")
    
    logger.info(f"Received registration request for email: {user.email}")
    
    try:
        statement = select(User).where(User.email == user.email)
        db_user = db.exec(statement).first()
        
        if db_user:
            logger.warning(f"Attempted registration with existing email: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        db_user = User(email=user.email)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        magic_token = create_magic_token(user_id=db_user.id)
        
        try:
            await send_magic_link(user.email, magic_token)
            logger.info(f"Magic link sent to: {user.email}")
        except Exception as e:
            logger.error(f"Failed to send magic link: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to send magic link")
        
        return {"msg": "Success! Check your email for your login link."}
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise 

@router.post("/login")
async def login_user(
    request: Request,
    user: UserLogin, 
    db: Session = Depends(get_db)
):
    statement = select(User).where(User.email == user.email)
    db_user = db.exec(statement).first()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Email not registered")
    
    magic_token = create_magic_token(user_id=db_user.id)
    
    # Get frontend URL from request headers, fallback to origin, then default
    frontend_url = request.headers.get('referer') or request.headers.get('origin') or DEFAULT_FRONTEND_URL
    
    try:
        await send_magic_link(user.email, magic_token, frontend_url)
    except Exception as e:
        logger.error(f"Failed to send magic link email: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send magic link email")
    
    return {"msg": "Check your email for your login link."}

@router.get("/verify", response_model=Token)
async def verify_magic_link(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.exec(select(User).where(User.id == int(user_id))).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        access_token = create_magic_token(user_id=user.id)
        return {"access_token": access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/me", response_model=UserMeResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user 