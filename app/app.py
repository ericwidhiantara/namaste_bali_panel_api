from typing import List

from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.cors import CORSMiddleware

from app.controller.auth_controller import AuthController
from app.handler.http_handler import CustomHttpException, custom_exception
from app.models.schemas import FormUserModel, TokenSchema, SystemUser, UserModel, BaseResp
from app.utils.deps import get_current_user

app = FastAPI()
app.add_exception_handler(CustomHttpException, custom_exception)
# app.add_exception_handler(404, not_found_handler)

auth_controller = AuthController()


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


@app.post('/register', summary="Create new user", response_model=UserModel)
async def register(data: FormUserModel = Depends()):
    return await auth_controller.register(data)


@app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await auth_controller.login(form_data)


@app.get('/me', summary='Get details of currently logged in user', response_model=BaseResp[SystemUser])
async def get_me(user: SystemUser = Depends(get_current_user)):

    return BaseResp[SystemUser](data=user)


@app.get("/users", summary='Get all users', response_model=BaseResp[List[UserModel]], dependencies=[Depends(get_current_user)])
async def get_users():
    users = await auth_controller.get_users()

    if not users:
        raise CustomHttpException(
            status_code=404,
            message="No users found"
        )
    return BaseResp[List[UserModel]](data=users)
