import uuid
import os
from typing import Optional, Tuple
from minio import Minio
from minio.error import S3Error
from fastapi import HTTPException
from io import BytesIO

from app.config.minio_config import MinIOConfig


class MinIOService:
    """Service for interacting with MinIO object storage"""
    
    def __init__(self):
        self.client = Minio(
            MinIOConfig.ENDPOINT,
            access_key=MinIOConfig.ACCESS_KEY,
            secret_key=MinIOConfig.SECRET_KEY,
            secure=MinIOConfig.SECURE
        )
        self.bucket = MinIOConfig.BUCKET
        
        # Auto-create bucket if it doesn't exist
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                # Make bucket public for public images read
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": ["s3:GetObject"],
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Resource": [f"arn:aws:s3:::{self.bucket}/*"]
                        }
                    ]
                }
                import json
                self.client.set_bucket_policy(self.bucket, json.dumps(policy))
                print(f"✅ Created MinIO bucket: {self.bucket} with public read policy")
            else:
                print(f"✅ MinIO bucket '{self.bucket}' already exists")
        except Exception as e:
            print(f"⚠️  MinIO bucket check/creation warning: {str(e)}")
    
    def upload_file(self, file_content, filename: str, content_type: str = "application/octet-stream") -> str:
        """
        Upload file to MinIO
        
        Args:
            file_content: bytes or file-like object
            filename: Full path/filename in bucket (e.g. 'uploads/destinations/tanah-lot/image.png')
            content_type: MIME type
        
        Returns:
            object_name: Full path in MinIO
        """
        try:
            if isinstance(file_content, bytes):
                file_size = len(file_content)
                file_object = BytesIO(file_content)
            else:
                # Assuming it's a file-like object (like from FastAPI UploadFile)
                file_content.seek(0, 2)
                file_size = file_content.tell()
                file_content.seek(0)
                file_object = file_content
            
            # Upload to MinIO
            self.client.put_object(
                self.bucket,
                filename,
                file_object,
                file_size,
                content_type=content_type
            )
            
            print(f"✅ Successfully uploaded to MinIO: {filename} ({file_size} bytes)")
            return filename
            
        except S3Error as e:
            print(f"❌ MinIO S3 Error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file to MinIO: {str(e)}"
            )
        except Exception as e:
            print(f"❌ Upload Error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error uploading to MinIO: {str(e)}"
            )
    
    def delete_file(self, object_name: str):
        """
        Delete file from MinIO
        
        Args:
            object_name: Full object path in MinIO
        """
        try:
            self.client.remove_object(self.bucket, object_name)
            return True
        except S3Error as e:
            print(f"Error deleting file from Minio: {str(e)}")
            return False
            
    def get_public_url(self, object_name: str) -> str:
        """
        Get public URL for a file in MinIO
        """
        base = os.getenv("BASE_URL")
        if base:
            # Use public base URL proxy if configured
            return f"{base.rstrip('/')}/file/{object_name}"
            
        endpoint = MinIOConfig.ENDPOINT
        protocol = "https" if MinIOConfig.SECURE else "http"
        return f"{protocol}://{endpoint}/{self.bucket}/{object_name}"
