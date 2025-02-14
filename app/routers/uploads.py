from fastapi import APIRouter, UploadFile, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime, UTC
import shutil
import uuid
import aiofiles
from typing import Optional
from ..database import get_db
from ..models.user import User
from ..models.upload import Upload
from ..auth import get_current_user  # Assuming you have auth middleware
import logging

router = APIRouter()

class Settings:
    BASE_DIR = Path(__file__).resolve().parent.parent
    UPLOAD_DIR = BASE_DIR / "uploads"
    PDF_DIR = UPLOAD_DIR / "pdfs"
    TEMP_DIR = UPLOAD_DIR / "temp"
    MAX_FILE_SIZE = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {".pdf"}
    
    @classmethod
    def initialize(cls):
        for directory in [cls.UPLOAD_DIR, cls.PDF_DIR, cls.TEMP_DIR]:
            directory.mkdir(exist_ok=True)

settings = Settings()
settings.initialize()

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename while preserving the original extension."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    extension = Path(original_filename).suffix
    return f"{timestamp}_{unique_id}{extension}"

async def save_upload_file(upload_file: UploadFile) -> tuple[Path, str]:
    """Save an uploaded file to the temporary directory and return its path."""
    temp_path = settings.TEMP_DIR / generate_unique_filename(upload_file.filename)
    
    try:
        async with aiofiles.open(temp_path, 'wb') as out_file:
            while content := await upload_file.read(1024 * 1024):  # Read in 1MB chunks
                await out_file.write(content)
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    return temp_path, upload_file.filename

def validate_file(file: UploadFile) -> None:
    """Validate file type and size."""
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Check content type
    if file.content_type != 'application/pdf':
        raise HTTPException(
            status_code=400,
            detail="Invalid content type. Only PDFs are allowed."
        )

def move_to_permanent_storage(temp_path: Path, original_filename: str) -> Path:
    """Move file from temporary to permanent storage."""
    permanent_path = settings.PDF_DIR / generate_unique_filename(original_filename)
    try:
        shutil.move(str(temp_path), str(permanent_path))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to move file to permanent storage: {str(e)}"
        )
    return permanent_path

def cleanup_temp_files() -> int:
    """Remove all files from temporary directory. Returns count of files removed."""
    count = 0
    for file_path in settings.TEMP_DIR.glob("*"):
        if file_path.is_file():
            try:
                file_path.unlink()
                count += 1
            except Exception:
                logger.exception(f"Failed to delete temporary file: {file_path}")
    return count

# Set up logging
logger = logging.getLogger(__name__)

@router.post("/")
def upload_file(
    file: UploadFile,
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        validate_file(file)
        temp_path, original_filename = save_upload_file(file)
        permanent_path = move_to_permanent_storage(temp_path, original_filename)
        
        upload = Upload(
            user_id=current_user.id,
            file_path=str(permanent_path.relative_to(settings.BASE_DIR)),
            original_filename=original_filename,
            file_size=permanent_path.stat().st_size,
            mime_type=file.content_type,
            description=description,
            upload_date=datetime.now(UTC)
        )
        
        db.add(upload)
        db.commit()
        
        return {
            "message": "File uploaded successfully",
            "upload_id": upload.id,
            "file_path": upload.file_path
        }
        
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def list_user_uploads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all uploads for the current user."""
    uploads = db.query(Upload).filter(Upload.user_id == current_user.id).all()
    return {
        "uploads": [
            {
                "id": upload.id,
                "filename": upload.original_filename,
                "size": upload.file_size,
                "uploaded_at": upload.upload_date,
                "description": upload.description
            }
            for upload in uploads
        ]
    }

@router.delete("/{upload_id}")
def delete_upload(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific upload."""
    upload = db.query(Upload).filter(
        Upload.id == upload_id,
        Upload.user_id == current_user.id
    ).first()
    
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Delete the physical file
    file_path = settings.BASE_DIR / upload.file_path
    if file_path.exists():
        file_path.unlink()
    
    db.delete(upload)
    db.commit()
    
    return {"message": "Upload deleted successfully"}
