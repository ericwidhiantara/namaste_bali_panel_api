import os
import uuid
from datetime import datetime

from fastapi import FastAPI, status
from pymongo import MongoClient

from app.handler.http_handler import CustomHttpException
from app.models.teams import FormTeamModel, FormEditTeamModel
from app.utils.helper import save_picture

# Connect to MongoDB
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION = "teams"

app = FastAPI()


class TeamController:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db[COLLECTION]

    async def get_teams(self):
        teams = self.collection.find()

        items = []
        # Iterate the teams
        for team in teams:
            # append the team to the items
            items.append(team)

        print("ini teams", teams)

        return [team for team in items]

    async def get_teams_pagination(self, page_number=1, page_size=10, search=None):
        # Calculate the skip value based on page_number and page_size
        skip = (page_number - 1) * page_size

        # Fetch teams from the database with pagination
        teams = self.collection.find({
            '$or': [
                {'name': {'$regex': search, '$options': 'i'}},
                {'whatsapp': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}},
                {'address': {'$regex': search, '$options': 'i'}},
            ]
        }).skip(skip).limit(page_size).sort('created_at', -1)

        items = []
        # Iterate the teams
        for project in teams:
            # set the images to the project
            project.pop("_id")

            # append the project to the items
            items.append(project)
            print("items", items)

        # Count total teams for pagination
        total_teams = self.collection.count_documents({
            '$or': [
                {'name': {'$regex': search, '$options': 'i'}},
                {'whatsapp': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}},
                {'address': {'$regex': search, '$options': 'i'}},
            ]
        })

        # Calculate total pages
        total_pages = (total_teams + page_size - 1) // page_size

        # Prepare JSON response
        response = {
            "page_number": page_number,
            "page_size": page_size,
            "total": total_teams,
            "total_pages": total_pages,
            "teams": items
        }

        print("ini response", response)
        return response

    async def create_team(self, data: FormTeamModel):
        # iterate the data.image
        upload_dir = "/teams/" + data.name.lower().replace(" ", "-")

        # Save picture
        picture_path = save_picture(upload_dir, data.image)
        if picture_path == "File extension not allowed":
            raise CustomHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="File extension not allowed"
            )

        # Create new team
        team = {
            "id": str(uuid.uuid4()),
            "name": data.name,
            "email": data.email,
            "whatsapp": data.whatsapp,
            "facebook": data.facebook,
            "instagram": data.instagram,
            "twitter": data.twitter,
            "tiktok": data.tiktok,
            "role": data.role,
            "address": data.address,
            "image": picture_path,
            "created_at": int(datetime.now().timestamp()),
            "updated_at": int(datetime.now().timestamp()),
        }
        # Insert team into MongoDB
        self.collection.insert_one(team)

        # set item from team
        item = team

        return item

    async def edit_team(self, data: FormEditTeamModel):

        item = self.collection.find_one({"id": data.id})
        if not item:
            raise CustomHttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Team not found"
            )

        upload_dir = "/teams/" + data.name.lower().replace(" ", "-")

        # Save picture
        picture_path = save_picture(upload_dir, data.image)
        if picture_path == "File extension not allowed":
            raise CustomHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="File extension not allowed"
            )

        # Create new team
        team = {
            "name": data.name,
            "email": data.email,
            "whatsapp": data.whatsapp,
            "facebook": data.facebook if data.facebook else item.get("facebook"),
            "instagram": data.instagram if data.instagram else item.get("instagram"),
            "twitter": data.twitter if data.twitter else item.get("twitter"),
            "tiktok": data.tiktok if data.tiktok else item.get("tiktok"),
            "role": data.role,
            "address": data.address,
            "image": picture_path,
            "created_at": int(datetime.now().timestamp()),
            "updated_at": int(datetime.now().timestamp()),
        }

        print("ini team", team)
        # Update team into MongoDB
        self.collection.update_one({"id": data.id}, {"$set": team})
        updated = self.collection.find_one({"id": data.id})

        # set item from updated data
        item = updated

        return item

    async def delete_team(self, team_id: str):

        item = self.collection.find_one({"id": team_id})
        if not item:
            raise CustomHttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Team not found"
            )

        # Delete team from MongoDB
        self.collection.delete_one({"id": team_id})
        return None
