from pydantic import BaseModel, EmailStr, validator

class UserModel(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    username: str
    password: str

@validator("password_confirmation")
def passwords_match(cls, v, values, **kwargs):
    if "password" in values and v != values["password"]:
        raise ValueError("passwords do not match")
    return v