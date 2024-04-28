from collections import defaultdict
from typing import List

from fastapi import FastAPI, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.controller.auth_controller import AuthController
from app.controller.destination_controller import DestinationController
from app.controller.order_controller import OrderController
from app.controller.team_controller import TeamController
from app.controller.user_controller import UserController
from app.handler.http_handler import CustomHttpException, custom_exception
from app.models.destinations import DestinationModel, FormDestinationModel, FormEditDestinationModel, \
    DestinationPaginationModel
from app.models.orders import OrderModel, FormOrderModel, FormEditOrderModel, \
    OrderPaginationModel
from app.models.schemas import TokenSchema, BaseResp, Meta
from app.models.teams import TeamModel, FormTeamModel, FormEditTeamModel, TeamPaginationModel
from app.models.users import FormEditUserModel, \
    UserPaginationModel
from app.models.users import FormUserModel, SystemUser, UserModel
from app.utils.deps import get_current_user
from app.utils.helper import get_object_url

app = FastAPI()
app.add_exception_handler(CustomHttpException, custom_exception)
# app.add_exception_handler(404, not_found_handler)

auth_controller = AuthController()
destination_controller = DestinationController()
team_controller = TeamController()
user_controller = UserController()
order_controller = OrderController()


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


@app.get("/destinations", summary='Get all destination', response_model=BaseResp[DestinationPaginationModel],
         dependencies=[Depends(get_current_user)])
async def get_destinations(page: int = Query(1, gt=0), limit: int = Query(10, gt=0), search: str = Query(None)):
    result = await destination_controller.get_destinations_pagination(page, limit, search)

    if result["destinations"] is None:
        raise CustomHttpException(
            status_code=404,
            message="No destinations found"
        )
    return BaseResp[DestinationPaginationModel](meta=Meta(message="Get all destination successfuly"), data=dict(result))


@app.get("/destinations/list", summary='Get all destination list', response_model=BaseResp[List[DestinationModel]])
async def get_destinations():
    result = await destination_controller.get_destinations()

    if not result:
        raise CustomHttpException(
            status_code=404,
            message="No destinations found"
        )
    return BaseResp[List[DestinationModel]](meta=Meta(message="Get all destination list successfuly"), data=result)


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


@app.get("/teams", summary='Get all team', response_model=BaseResp[TeamPaginationModel],
         dependencies=[Depends(get_current_user)])
async def get_teams(page: int = Query(1, gt=0), limit: int = Query(10, gt=0), search: str = Query(None)):
    result = await team_controller.get_teams_pagination(page, limit, search)

    if result["teams"] is None:
        raise CustomHttpException(
            status_code=404,
            message="No teams found"
        )
    return BaseResp[TeamPaginationModel](meta=Meta(message="Get all team successfuly"), data=dict(result))


@app.get("/teams/list", summary='Get all team list', response_model=BaseResp[List[TeamModel]])
async def get_teams():
    result = await team_controller.get_teams()

    if not result:
        raise CustomHttpException(
            status_code=404,
            message="No teams found"
        )
    return BaseResp[List[TeamModel]](meta=Meta(message="Get all team list successfuly"), data=result)


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


@app.get("/users", summary='Get all user', response_model=BaseResp[UserPaginationModel],
         dependencies=[Depends(get_current_user)])
async def get_users(page: int = Query(1, gt=0), limit: int = Query(10, gt=0), search: str = Query(None)):
    result = await user_controller.get_users_pagination(page, limit, search)

    if result["users"] is None:
        raise CustomHttpException(
            status_code=404,
            message="No users found"
        )
    return BaseResp[UserPaginationModel](meta=Meta(message="Get all user successfuly"), data=dict(result))


@app.get("/users/list", summary='Get all user list', response_model=BaseResp[List[UserModel]],
         dependencies=[Depends(get_current_user)])
async def get_users():
    result = await user_controller.get_users()

    if not result:
        raise CustomHttpException(
            status_code=404,
            message="No users found"
        )
    return BaseResp[List[UserModel]](meta=Meta(message="Get all user list successfuly"), data=result)


@app.post('/users', summary="Create new user", response_model=BaseResp[UserModel],
          dependencies=[Depends(get_current_user)])
async def create_user(data: FormUserModel = Depends(), ):
    res = await user_controller.create_user(data)
    return BaseResp[UserModel](meta=Meta(message="Create user successfully"), data=res)


@app.patch('/users', summary="Update user", response_model=BaseResp[UserModel],
           dependencies=[Depends(get_current_user)])
async def edit_user(data: FormEditUserModel = Depends()):
    res = await user_controller.edit_user(data)

    return BaseResp[UserModel](meta=Meta(message="Update user successfully"), data=res)


@app.delete('/users/{user_id}', summary="Delete user", response_model=BaseResp,
            dependencies=[Depends(get_current_user)])
async def delete_user(user_id: str):
    await user_controller.delete_user(user_id)

    return BaseResp(meta=Meta(message="Delete user successfully"))


@app.get("/orders", summary='Get all order', response_model=BaseResp[OrderPaginationModel],
         dependencies=[Depends(get_current_user)])
async def get_orders(page: int = Query(1, gt=0), limit: int = Query(10, gt=0), search: str = Query(None)):
    result = await order_controller.get_orders_pagination(page, limit, search)

    print("ini result", result)
    if result["orders"] is None:
        raise CustomHttpException(
            status_code=404,
            message="No orders found"
        )
    return BaseResp[OrderPaginationModel](meta=Meta(message="Get all order successfuly"), data=dict(result))


@app.get("/orders/list", summary='Get all order list', response_model=BaseResp[List[OrderModel]],
         dependencies=[Depends(get_current_user)])
async def get_orders():
    result = await order_controller.get_orders()

    if not result:
        raise CustomHttpException(
            status_code=404,
            message="No orders found"
        )
    return BaseResp[List[OrderModel]](meta=Meta(message="Get all order list successfuly"), data=result)


@app.post('/orders', summary="Create new order", response_model=BaseResp[OrderModel],
          dependencies=[Depends(get_current_user)])
async def create_order(data: FormOrderModel = Depends(), ):
    res = await order_controller.create_order(data)
    return BaseResp[OrderModel](meta=Meta(message="Create order successfully"), data=res)


@app.patch('/orders', summary="Update order", response_model=BaseResp[OrderModel],
           dependencies=[Depends(get_current_user)])
async def edit_order(data: FormEditOrderModel = Depends()):
    res = await order_controller.edit_order(data)

    return BaseResp[OrderModel](meta=Meta(message="Update order successfully"), data=res)


@app.delete('/orders/{order_id}', summary="Delete order", response_model=BaseResp,
            dependencies=[Depends(get_current_user)])
async def delete_order(order_id: str):
    await order_controller.delete_order(order_id)

    return BaseResp(meta=Meta(message="Delete order successfully"))
