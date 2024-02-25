from pydantic import BaseModel, EmailStr, field_validator


class UserModel(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    username: str
    password: str


@field_validator("password_confirmation")
def passwords_match(v, values):
    if "password" in values and v != values["password"]:
        raise ValueError("passwords do not match")
    return v
