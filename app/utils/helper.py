import os

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


def allowed_file(file):
    return '.' in file and file.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_picture(file):
    if file.filename == "":
        return ""

    if not allowed_file(file.filename):
        return "File extension not allowed"

    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    print("file path", file_path)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_path


def delete_picture(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
