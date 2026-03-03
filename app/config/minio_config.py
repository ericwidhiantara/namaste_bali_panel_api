import os
from minio import Minio

class MinIOConfig:
    """MinIO configuration and client initialization"""
    
    ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000").replace("http://", "").replace("https://", "")
    ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    BUCKET = os.getenv("MINIO_BUCKET", "namaste-bali")
    SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
    
    @classmethod
    def get_client(cls) -> Minio:
        """Create and return MinIO client instance"""
        return Minio(
            cls.ENDPOINT,
            access_key=cls.ACCESS_KEY,
            secret_key=cls.SECRET_KEY,
            secure=cls.SECURE
        )
