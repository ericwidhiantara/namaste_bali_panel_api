import os
from fastapi import Form
from app.services.minio_service import MinIOService

def form_body(cls):
    cls.__signature__ = cls.__signature__.replace(
        parameters=[
            arg.replace(default=Form(...))
            for arg in cls.__signature__.parameters.values()
        ]
    )
    return cls

UPLOAD_DIRECTORY = "uploads"  # Prefix for MinIO objects
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}  # Specify the allowed image file extensions

def allowed_file(file_name):
    if not getattr(file_name, "rsplit", None):
        if hasattr(file_name, "filename"):
            file_name = file_name.filename
        else:
            return False
            
    return '.' in file_name and file_name.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_picture(directory, file):
    """
    Save picture to MinIO.
    """
    if not getattr(file, "filename", None) or file.filename == "":
        return ""

    if not allowed_file(file):
        return "File extension not allowed"

    try:
        minio_service = MinIOService()
        
        # Build object name (e.g. uploads/destinations/tanah-lot/image.png)
        # remove leading slashes from directory to prevent double slashes
        dir_clean = directory.lstrip('/')
        object_name = f"{UPLOAD_DIRECTORY}/{dir_clean}/{file.filename}"
        
        # Ensure file content is uploaded
        minio_service.upload_file(
            file.file, 
            object_name, 
            getattr(file, 'content_type', 'application/octet-stream')
        )
        
        return object_name
    except Exception as e:
        print("Error saving file to MinIO:", e)
        return None

def delete_picture(file_path):
    """
    Delete picture from MinIO.
    """
    try:
        minio_service = MinIOService()
        return minio_service.delete_file(file_path)
    except Exception as e:
        print("Error deleting file from MinIO:", e)
        return False

def get_object_url(file_path):
    """
    Generate a URL for an object in MinIO.
    """
    if not file_path:
        return ""
        
    try:
        minio_service = MinIOService()
        return minio_service.get_public_url(file_path)
    except Exception as e:
        print("Error getting MinIO URL:", e)
        base_url = os.getenv("BASE_URL")
        if base_url:
            return f"{base_url.rstrip('/')}/{file_path}"
        return f"/{file_path}"
