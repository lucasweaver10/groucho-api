import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request, status, BackgroundTasks
from fastapi.security import HTTPBearer, OAuth2PasswordBearer, OAuth2PasswordRequestForm
import logging
import sys
from .schemas.user import User
from .schemas.token import Token
from .auth import create_access_token, get_current_user
from .database import engine, get_db
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, content, content_briefs, content_sections, events, uploads, agents, webhooks
from .auth import (
    get_current_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from contextlib import asynccontextmanager
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):    
    print("Starting up...")    
    yield
    print("Shutting down...")    

app = FastAPI(lifespan=lifespan)

load_dotenv()
logger = logging.getLogger(__name__)
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3007")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[        
        os.getenv("FRONTEND_URL", "http://localhost:3007")
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Database
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Update app startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Security
security = HTTPBearer()

# You'll need to set these environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(content.router, prefix="/contents", tags=["contents"])
app.include_router(content_briefs.router, prefix="/content-briefs", tags=["content-briefs"])
app.include_router(content_sections.router, prefix="/content-sections", tags=["content-sections"])

@app.get("/")
async def root():    
    return {"message": "Welcome to Groucho API"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    try:
        if request.method != "OPTIONS":  # Only try to read body for non-OPTIONS requests
            body = await request.body()
            logger.info(f"Request body: {body.decode()}")
    except Exception as e:
        logger.error(f"Error reading request body: {str(e)}")
    
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    
    return response
