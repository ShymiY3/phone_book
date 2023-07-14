from pydantic import BaseModel, EmailStr
from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from .utils import Hasher
from ..exceptions import FormException
from . import crud

class UserBase(BaseModel):
    username: str
    email: EmailStr
    
class UserInput(UserBase):
    password: str
    confirm_password: str
    
    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...)
    ):
        return cls(
            username=username, 
            email=email, 
            password=password,
            confirm_password=confirm_password)
    
    def clean_user(self):
        self.password = Hasher.get_password_hash(self.password)
        self.confirm_password = Hasher.get_password_hash(self.confirm_password)
        return self
    
    def is_valid(self, db):
        if len(self.password) < 6:
            raise FormException(status_code=400, detail="Password must have 6 characters")
        if not self.password == self.confirm_password:
            raise FormException(status_code=400, detail="Passwords don't match")
        if crud.get_user_by_username(db, self.username):
            raise FormException(status_code=400, detail="Username already taken")
        if crud.get_user_by_email(db, self.email):
            raise FormException(status_code=400, detail="Email in use")
        return True

class UserLogin(BaseModel):
    username: str
    password: str
    
    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        password: str = Form(...),
    ):
        return cls(
            username=username,
            password=password)


class UserLoginToken(OAuth2PasswordRequestForm):
    def is_valid(self, db):
        user = crud.get_user_by_username(db, self.username)
        if not user:
            raise FormException(status_code=400, detail="Username and password don't match")
        if not Hasher.verify_password(self.password, user.password):
            raise FormException(status_code=400, detail="Username and password don't match")
        return True
    
    
class TokenSchema(BaseModel):
    access_token: str
    token_type: str