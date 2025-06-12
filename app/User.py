from pydantic import BaseModel


class User(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    avatar: str


class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    avatar: str
    password: str


class LoginData(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    token: str
