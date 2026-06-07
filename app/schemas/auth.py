from pydantic import BaseModel
from pydantic import EmailStr
from app.models.roles import Role


class UserRegister(BaseModel):

    username: str

    email: EmailStr

    password: str

    role: Role


class UserLogin(BaseModel):

    username: str

    password: str


class TokenResponse(BaseModel):

    access_token: str

    token_type: str