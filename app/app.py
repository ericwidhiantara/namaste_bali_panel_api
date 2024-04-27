from collections import defaultdict
from typing import List

from fastapi import FastAPI, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.controller.auth_controller import AuthController
from app.controller.destination_controller import DestinationController
from app.controller.team_controller import TeamController
from app.handler.http_handler import CustomHttpException, custom_exception
from app.models.destinations import DestinationModel, FormDestinationModel, FormEditDestinationModel
from app.models.teams import TeamModel, FormTeamModel, FormEditTeamModel
from app.models.schemas import TokenSchema, BaseResp, Meta
from app.models.users import FormUserModel, SystemUser, UserModel
from app.utils.deps import get_current_user
from app.utils.helper import get_object_url

app = FastAPI()
app.add_exception_handler(CustomHttpException, custom_exception)
# app.add_exception_handler(404, not_found_handler)

auth_controller = AuthController()
destination_controller = DestinationController()
team_controller = TeamController()


@app.exception_handler(RequestValidationError)
async def custom_form_validation_error(_, exc):
    reformatted_message = defaultdict(list)
    for pydantic_error in exc.errors():
        loc, msg = pydantic_error["loc"], pydantic_error["msg"]
        filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc
        field_string = ".".join(filtered_loc)  # nested fields with dot-notation
        reformatted_message[field_string].append(msg)

    print("ini reformatted_message", reformatted_message)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(

            {"meta": {
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "Validation error",
                "error": True
            }, "data": reformatted_message}
        ),
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"]
)


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url='/docs')


@app.post('/register', summary="Create new user", response_model=BaseResp[UserModel])
async def register(data: FormUserModel = Depends()):
    print("ini data di register", data)
    result = await auth_controller.register(data)
    return BaseResp[UserModel](meta=Meta(message="Register success"), data=result)


@app.post('/login', summary="Create access and refresh tokens for user", response_model=BaseResp[TokenSchema])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    result = await auth_controller.login(form_data)
    return BaseResp[TokenSchema](meta=Meta(message="Login success"), data=result)


@app.get('/me', summary='Get details of currently logged in user', response_model=BaseResp[SystemUser])
async def get_me(user: SystemUser = Depends(get_current_user)):
    return BaseResp[SystemUser](meta=Meta(message="Get user login data successfully"), data=user)


@app.get('/get-picture', summary='Get picture of currently logged in user', response_model=str,
         dependencies=[Depends(get_current_user)])
async def get_picture(user: SystemUser = Depends(get_current_user)):
    return get_object_url(user.picture)


@app.get("/users", summary='Get all users', response_model=BaseResp[List[UserModel]],
         dependencies=[Depends(get_current_user)])
async def get_users():
    users = await auth_controller.get_users()

    if not users:
        raise CustomHttpException(
            status_code=404,
            message="No users found"
        )
    return BaseResp[List[UserModel]](meta=Meta(message="Get all user successfully"), data=users)


@app.get("/destinations", summary='Get all destination', response_model=BaseResp[List[DestinationModel]],
         dependencies=[Depends(get_current_user)])
async def get_destinations():
    result = await destination_controller.get_destinations()

    if not result:
        raise CustomHttpException(
            status_code=404,
            message="No destinations found"
        )
    return BaseResp[List[DestinationModel]](meta=Meta(message="Get all destination successfuly"), data=result)


@app.post('/destinations', summary="Create new destination", response_model=BaseResp[DestinationModel],
          dependencies=[Depends(get_current_user)])
async def create_destination(data: FormDestinationModel = Depends(), ):
    res = await destination_controller.create_destination(data)
    return BaseResp[DestinationModel](meta=Meta(message="Create destination successfully"), data=res)


@app.patch('/destinations', summary="Update destination", response_model=BaseResp[DestinationModel],
           dependencies=[Depends(get_current_user)])
async def edit_destination(data: FormEditDestinationModel = Depends()):
    res = await destination_controller.edit_destination(data)

    return BaseResp[DestinationModel](meta=Meta(message="Update destination successfully"), data=res)


@app.delete('/destinations/{destination_id}', summary="Delete destination", response_model=BaseResp,
            dependencies=[Depends(get_current_user)])
async def delete_destination(destination_id: str):
    await destination_controller.delete_destination(destination_id)

    return BaseResp(meta=Meta(message="Delete destination successfully"))


@app.get("/teams", summary='Get all team', response_model=BaseResp[List[TeamModel]],
         dependencies=[Depends(get_current_user)])
async def get_teams():
    result = await team_controller.get_teams()

    if not result:
        raise CustomHttpException(
            status_code=404,
            message="No teams found"
        )
    return BaseResp[List[TeamModel]](meta=Meta(message="Get all team successfuly"), data=result)


@app.post('/teams', summary="Create new team", response_model=BaseResp[TeamModel],
          dependencies=[Depends(get_current_user)])
async def create_team(data: FormTeamModel = Depends(), ):
    res = await team_controller.create_team(data)
    return BaseResp[TeamModel](meta=Meta(message="Create team successfully"), data=res)


@app.patch('/teams', summary="Update team", response_model=BaseResp[TeamModel],
           dependencies=[Depends(get_current_user)])
async def edit_team(data: FormEditTeamModel = Depends()):
    res = await team_controller.edit_team(data)

    return BaseResp[TeamModel](meta=Meta(message="Update team successfully"), data=res)


@app.delete('/teams/{team_id}', summary="Delete team", response_model=BaseResp,
            dependencies=[Depends(get_current_user)])
async def delete_team(team_id: str):
    await team_controller.delete_team(team_id)

    return BaseResp(meta=Meta(message="Delete team successfully"))
