import os
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, status, UploadFile, Form
from pymongo import MongoClient

from app.handler.http_handler import CustomHttpException
from app.models.schemas import FormPortfolioModel, FormEditPortfolioModel, FormDeletePortfolioModel
from app.utils.helper import save_picture, get_object_url

# Connect to MongoDB
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION = "projects"
IMAGE_COLLECTION = "project_images"

app = FastAPI()


class PortfolioController:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db[COLLECTION]
        self.image_collection = self.db[IMAGE_COLLECTION]

    async def get_projects(self):
        projects = self.collection.find()

        items = []
        # Iterate the projects
        for project in projects:
            images = self.image_collection.find({"project_id": project["id"]}).sort('created_at', -1)

            # set the images to the project
            project["images"] = []

            # iterate the images
            for image in images:
                # set the image path to aws s3 url
                image["image_path"] = get_object_url(image["image_path"])
                # append the image to the project
                project["images"].append(image)

            # append the project to the items
            items.append(project)

        print("ini projects", projects)

        return [project for project in items]

    async def get_projects_pagination(self, page_number=1, page_size=10, search=None):
        # Calculate the skip value based on page_number and page_size
        skip = (page_number - 1) * page_size

        # Fetch projects from the database with pagination
        projects = self.collection.find({
            '$or': [
                {'title': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        }).skip(skip).limit(page_size).sort('created_at', -1)

        items = []
        # Iterate the projects
        for project in projects:
            images = self.image_collection.find({"project_id": project["id"]})

            # set the images to the project
            project["images"] = []
            project.pop("_id")

            # iterate the images
            for image in images:
                image.pop("_id")
                # set the image path to aws s3 url
                image["image_path"] = get_object_url(image["image_path"])
                # append the image to the project
                project["images"].append(image)

            # append the project to the items
            items.append(project)
            print("items", items)

        # Count total projects for pagination
        total_projects = self.collection.count_documents({})

        # Calculate total pages
        total_pages = (total_projects + page_size - 1) // page_size

        # Prepare JSON response
        response = {
            "page_number": page_number,
            "page_size": page_size,
            "total": total_projects,
            "total_pages": total_pages,
            "projects": items
        }

        print("ini response", response)
        return response

    async def create_project(self, data: FormPortfolioModel,
                             images: List[UploadFile] = Form(..., description="portfolio picture")):
        # iterate the data.picture
        uploaded_pictures = []
        upload_dir = "/projects/" + data.title.lower().replace(" ", "-")
        for file in images:
            res = save_picture(upload_dir, file)
            if res == "File not allowed":
                raise CustomHttpException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="File not allowed"
                )
            uploaded_pictures.append(res)

        # Create new project
        project = {
            "id": str(uuid.uuid4()),
            "title": data.title,
            "slug": data.title.lower().replace(" ", "-"),
            "description": data.description,
            "date_started": data.date_started,
            "date_finished": data.date_finished,
            "created_at": int(datetime.now().timestamp()),
            "updated_at": int(datetime.now().timestamp()),
        }
        # Insert project into MongoDB
        self.collection.insert_one(project)

        for image in uploaded_pictures:
            self.image_collection.insert_one({
                "id": str(uuid.uuid4()),
                "project_id": project["id"],
                "image_path": image
            })

        # set item from project
        item = project

        # get the images from mongo
        images = self.image_collection.find({"project_id": item["id"]})
        # set the images to the project
        item["images"] = []
        # iterate the images
        for image in images:
            # set the image path to aws s3 url
            image["image_path"] = get_object_url(image["image_path"])
            # append the image to the project
            item["images"].append(image)

        return item

    async def edit_project(self, data: FormEditPortfolioModel,
                           images: Optional[List[UploadFile]] = Form(None, description="portfolio picture")):

        item = self.collection.find_one({"id": data.id})
        if not item:
            raise CustomHttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Project not found"
            )
        # iterate the data.picture
        uploaded_pictures = []
        upload_dir = "/projects/" + data.title.lower().replace(" ", "-")

        if images is not None:
            for file in images:
                res = save_picture(upload_dir, file)
                if res == "File extension not allowed":
                    raise CustomHttpException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="File extension not allowed"
                    )
                uploaded_pictures.append(res)

        # Create new project
        project = {
            "title": data.title if data.title else item["title"],
            "slug": data.title.lower().replace(" ", "-"),
            "description": data.description if data.description else item["description"],
            "date_started": data.date_started if data.date_started else item["date_started"],
            "date_finished": data.date_finished if data.date_finished else item["date_finished"],
            "updated_at": int(datetime.now().timestamp()),
        }

        for image in uploaded_pictures:
            self.image_collection.insert_one({
                "id": str(uuid.uuid4()),
                "project_id": data.id,
                "image_path": image
            })

        print("ini project", project)
        # Update project into MongoDB
        self.collection.update_one({"id": data.id}, {"$set": project})
        updated = self.collection.find_one({"id": data.id})

        # set item from updated data
        item = updated
        # get the images from mongo
        images = self.image_collection.find({"project_id": item["id"]})
        # set the images to the item
        item["images"] = []
        # iterate the images
        for image in images:
            # set the image path to aws s3 url
            image["image_path"] = get_object_url(image["image_path"])
            # append the image to the item
            item["images"].append(image)

        return item

    async def delete_project(self, project_id: str):

        item = self.collection.find_one({"id": project_id})
        if not item:
            raise CustomHttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Project not found"
            )

        images = self.image_collection.find({"id": project_id})

        if images is not None:
            # print the image
            for image in images:
                print("ini file", image)
                # delete the image
                self.image_collection.delete_one({"id": image["id"]})

        # Delete project from MongoDB
        self.collection.delete_one({"id": project_id})
        return None

    def delete_single_image(self, image_id: str):
        item = self.image_collection.find_one({"id": image_id})
        if not item:
            raise CustomHttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Image not found"
            )

        self.image_collection.delete_one({"id": image_id})
        return None
