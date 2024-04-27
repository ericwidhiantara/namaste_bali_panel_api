from typing import TypeVar, Generic

from pydantic import BaseModel

M = TypeVar("M", bound=BaseModel)


class Meta(BaseModel):
    code: int = 200
    message: str = "OK"
    error: bool = False


class BaseResp(BaseModel, Generic[M]):
    meta: Meta = Meta()
    data: M = None  # support any object


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
