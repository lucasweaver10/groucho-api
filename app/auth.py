import os
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi import BackgroundTasks
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select
from .database import get_db
from .models.user import User
from .schemas.user import UserMeResponse
from .schemas.token import TokenData, Token
import logging
import resend
from .config import settings
from .config.email_config import get_email_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Environment variables
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
DEFAULT_FRONTEND_URL = "http://localhost:5173"

def get_domain_from_url(url: str) -> str:
    """Extract domain from URL."""
    from urllib.parse import urlparse
    try:
        domain = urlparse(url).netloc
        return domain.replace('www.', '')
    except:
        return "default"

def create_magic_token(user_id: int, expires_delta: Optional[timedelta] = None):
    to_encode = {"sub": str(user_id)}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def send_magic_link(email: str, token: str, frontend_url: str = DEFAULT_FRONTEND_URL):
    logger.info(f"Attempting to send magic link to email: {email}")
    logger.info(f"Frontend URL: {frontend_url}")
        
    # Remove trailing slash if present
    frontend_url = frontend_url.rstrip('/')
        
    # Get domain-specific email configuration
    config = get_email_config(frontend_url)
    
    if not config.get('api_key'):
        logger.error(f"No API key found for domain {get_domain_from_url(frontend_url)}")
        raise HTTPException(status_code=500, detail="Email service configuration error")
    
    logger.info(f"Selected email configuration: Domain={get_domain_from_url(frontend_url)}, API key={config['api_key'][:8]}...")
        
    # Set the API key for this request
    resend.api_key = config["api_key"]
        
    link = f"{frontend_url}/auth/callback?token={token}"
    logger.info(f"Generated magic link: {link}")
       
    try:
        if os.getenv("ENVIRONMENT") == "production":
            response = resend.Emails.send({
                "from": f"{config['from_name']} <{config['from_email']}>",
                "to": email,
                "subject": "Your Magic Login Link",
                "html": f"Click the link to login: <a href='{link}'>Login</a>"
            })
        
        logger.info(f"Email sent successfully to {email}.")
    
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise

    logger.info("send_magic_link function completed")

async def get_current_user_from_magic_link(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    statement = select(User).where(User.id == int(token_data.user_id))
    user = db.exec(statement).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None):
    to_encode = {"sub": str(user_id)}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    statement = select(User).where(User.id == int(token_data.user_id))
    user = db.exec(statement).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
