import os

import boto3
from fastapi import Form


def form_body(cls):
    cls.__signature__ = cls.__signature__.replace(
        parameters=[
            arg.replace(default=Form(...))
            for arg in cls.__signature__.parameters.values()
        ]
    )
    return cls


UPLOAD_DIRECTORY = "uploads"  # Specify the directory where you want to save the uploaded pictures
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}  # Specify the allowed image file extensions

# Set your AWS credentials
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

# Create an S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)


def allowed_file(file):
    return '.' in file and file.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#
# def save_picture(directory, file):
#     if file.filename == "":
#         return ""
#
#     if not allowed_file(file.filename):
#         return "File extension not allowed"
#
#     # Generate a unique file name in S3
#     s3_filename = os.path.join(UPLOAD_DIRECTORY + directory, file.filename)
#
#     try:
#         # Upload file to S3
#         s3.upload_fileobj(file.file, AWS_BUCKET_NAME, s3_filename)
#         print("ini object url", get_object_url(s3_filename))
#         return s3_filename
#     except Exception as e:
#         print("Error uploading file to S3:", e)
#         return None


def save_picture(directory, file):
    if file.filename == "":
        return ""

    if not allowed_file(file.filename):
        return "File extension not allowed"

    # Create the directory if it doesn't exist
    os.makedirs(UPLOAD_DIRECTORY+directory, exist_ok=True)

    try:
        # Save file to local directory
        file_path = os.path.join(UPLOAD_DIRECTORY+directory, file.filename)
        with open(file_path, 'wb') as f:
            f.write(file.file.read())

        # Return the path to the saved file
        return file_path
    except Exception as e:
        print("Error saving file locally:", e)
        return None


def delete_picture(file_path):
    try:
        # Delete the file from local filesystem
        os.remove(UPLOAD_DIRECTORY+file_path)
        return True
    except Exception as e:
        print("Error deleting file locally:", e)
        return False


def get_object_url(file_path):
    """
    Generate a URL for a local file.
    """
    # Retrieve the base URL from an environment variable
    base_url = os.getenv("BASE_URL")
    if not base_url:
        raise ValueError("BASE_URL environment variable is not set.")

    # Construct the URL by appending the file path relative to the served directory
    url = f"{base_url.rstrip('/')}/{file_path}"

    return url

#
# def delete_picture(file_path):
#     try:
#         # Extract bucket name and object key from file path
#         bucket_name, object_key = file_path.split('/', 1)
#
#         # Delete the object from S3
#         print("ini bucket", bucket_name)
#         print("ini object key", object_key)
#
#         s3.delete_object(Bucket=bucket_name, Key=object_key)
#         return True
#     except Exception as e:
#         print("Error deleting file from S3:", e)
#         return False
#
#
# def get_object_url(object_key):
#     """
#     Get the URL of an object in an S3 bucket.
#     """
#     try:
#         url = s3.generate_presigned_url(
#             'get_object',
#             Params={'Bucket': AWS_BUCKET_NAME, 'Key': object_key},
#             ExpiresIn=3600  # URL expiration time in seconds
#         )
#         return url
#     except Exception as e:
#         print("Error generating object URL:", e)
#         return None
