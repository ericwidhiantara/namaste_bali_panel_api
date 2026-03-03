import os
import io
import mimetypes
from minio import Minio
from app.config.minio_config import MinIOConfig

def seed_minio():
    """Uploads all local files in uploads/ to MinIO"""
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print(f"Directory {uploads_dir} not found.")
        return

    client = MinIOConfig.get_client()
    bucket = MinIOConfig.BUCKET

    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            # Make bucket public for public images read
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": ["s3:GetObject"],
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Resource": [f"arn:aws:s3:::{bucket}/*"]
                    }
                ]
            }
            import json
            client.set_bucket_policy(bucket, json.dumps(policy))
    except Exception as e:
        print(f"Error checking/creating bucket: {e}")

    for root, _, files in os.walk(uploads_dir):
        # Skip hidden files
        files = [f for f in files if not f.startswith('.')]
        
        for file in files:
            local_path = os.path.join(root, file)
            # object_name is the relative path from the current dir (e.g. uploads/destinations/...)
            object_name = local_path
            
            # Skip DS_Store and other unwanted files
            if file == ".DS_Store" or object_name.startswith("uploads/test/"):
                continue
                
            content_type, _ = mimetypes.guess_type(local_path)
            if not content_type:
                content_type = "application/octet-stream"
                
            try:
                # Check if it already exists
                try:
                    client.stat_object(bucket, object_name)
                    print(f"Skipping {object_name}, already exists in MinIO.")
                    continue
                except:
                    pass # Object doesn't exist, proceed to upload
                
                print(f"Uploading {object_name}...")
                client.fput_object(
                    bucket_name=bucket,
                    object_name=object_name,
                    file_path=local_path,
                    content_type=content_type
                )
            except Exception as e:
                print(f"Failed to upload {object_name}: {e}")

if __name__ == "__main__":
    print("Starting MinIO seed process...")
    seed_minio()
    print("MinIO seed complete!")
