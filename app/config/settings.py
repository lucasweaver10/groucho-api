import os
import boto3
import logging
from pydantic_settings import BaseSettings
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/essay_checker"
    
    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI settings
    OPEN_AI_API_KEY: Optional[str] = None
    OPEN_AI_MODEL: str = "gpt-4o-mini"
    
    # AWS/LocalStack Settings
    USE_LOCALSTACK: bool = os.getenv('USE_LOCALSTACK', 'True').lower() == 'true'
    AWS_REGION: str = os.getenv('AWS_REGION', 'us-west-2')
    SQS_QUEUE_NAME: str = "essay-checker-task-queue"
    
    @property
    def sqs_client(self):
        config = {
            'region_name': self.AWS_REGION,
        }
        
        if self.USE_LOCALSTACK:
            config.update({
                'endpoint_url': 'http://localstack:4566',
                'aws_access_key_id': 'test',
                'aws_secret_access_key': 'test'
            })
        else:
            config.update({
                'aws_access_key_id': os.getenv('SQS_AWS_ACCESS_KEY_ID'),
                'aws_secret_access_key': os.getenv('SQS_AWS_SECRET_ACCESS_KEY')
            })
            
        return boto3.client('sqs', **config)

    @property
    def SQS_QUEUE_URL(self) -> str:
        if self.USE_LOCALSTACK:
            return f"http://localstack:4566/000000000000/{self.SQS_QUEUE_NAME}"
        else:
            return f"https://sqs.{self.AWS_REGION}.amazonaws.com/{os.getenv('AWS_ACCOUNT_ID')}/{self.SQS_QUEUE_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Instantiate Settings
settings = Settings()
