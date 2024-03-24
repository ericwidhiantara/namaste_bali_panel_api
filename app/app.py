from typing import List

from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.cors import CORSMiddleware

from app.controller.auth_controller import AuthController
from app.controller.portfolio_controller import PortfolioController
from app.handler.http_handler import CustomHttpException, custom_exception
from app.models.schemas import FormUserModel, TokenSchema, SystemUser, UserModel, BaseResp, PortfolioModel, \
    FormPortfolioModel, FormEditPortfolioModel, Meta
from app.utils.deps import get_current_user

app = FastAPI()
app.add_exception_handler(CustomHttpException, custom_exception)
# app.add_exception_handler(404, not_found_handler)

auth_controller = AuthController()
project_controller = PortfolioController()


class WebsocketController:
    pass


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url='/docs')


@app.post('/register', summary="Create new user", response_model=BaseResp[UserModel])
async def register(data: FormUserModel = Depends()):
    print("ini data di register", data)
    result = await auth_controller.register(data)
    return BaseResp[UserModel](meta=Meta(message="Register success"),  data=result)


@app.post('/login', summary="Create access and refresh tokens for user", response_model=BaseResp[TokenSchema])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    result = await auth_controller.login(form_data)
    return BaseResp[TokenSchema](meta=Meta(message="Login success"),  data=result)


@app.get('/me', summary='Get details of currently logged in user', response_model=BaseResp[SystemUser])
async def get_me(user: SystemUser = Depends(get_current_user)):
    return BaseResp[SystemUser](meta=Meta(message="Get user login data successfully"), data=user)


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


@app.get("/projects", summary='Get all portfolio', response_model=BaseResp[List[PortfolioModel]],
         dependencies=[Depends(get_current_user)])
async def get_projects():
    result = await project_controller.get_projects()

    if not result:
        raise CustomHttpException(
            status_code=404,
            message="No projects found"
        )
    return BaseResp[List[PortfolioModel]](meta=Meta(message="Get all portfolio successfuly"),  data=result)


@app.post('/projects', summary="Create new portfolio", response_model=BaseResp[PortfolioModel],
          dependencies=[Depends(get_current_user)])
async def create_project(data: FormPortfolioModel = Depends()):
    res = await project_controller.create_project(data)
    return BaseResp[PortfolioModel](meta=Meta(message="Create portfolio successfully"), data=res)


@app.patch('/projects', summary="Update portfolio", response_model=BaseResp[PortfolioModel],
           dependencies=[Depends(get_current_user)])
async def edit_project(data: FormEditPortfolioModel = Depends()):
    res = await project_controller.edit_project(data)

    return BaseResp[PortfolioModel](meta=Meta(message="Update portfolio successfully"), data=res)
