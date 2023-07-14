from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..exceptions import FormException
from fastapi.templating import Jinja2Templates
from . import schemas, crud
from .utils import Token, OAuth2PasswordBearerWithCookie, Hasher
import os
from .models import User

router = APIRouter(prefix='/auth', tags=['AUTH'])

templates = Jinja2Templates(directory=os.path.join(os.getcwd(), 'phone_book', 'templates'))

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl='/auth/token')

@router.get('/register')
async def register(request: Request):
    return templates.TemplateResponse('auth/register.html', {'request': request})

@router.post('/register', response_class=RedirectResponse)
async def create_user(
    request: Request, 
    user: schemas.UserInput = Depends(schemas.UserInput.as_form),
    db: Session = Depends(get_db)
    ):
    if not user.is_valid(db):
        raise FormException(status_code=400, detail="Can't create user")
    
    user.clean_user()
    
    crud.create_user(db=db, user=user)
    return RedirectResponse('../../phone_book/?alert=success&mess=Created Successfully Log In', status_code=status.HTTP_302_FOUND)


@router.get('/login', response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse('auth/login.html', {'request': request})


@router.post('/token', response_model=schemas.TokenSchema)
async def token(
    response: Response, 
    credentials: schemas.UserLoginToken = Depends(), 
    db: Session = Depends(get_db)
    ):
    
    user = crud.get_user_by_username(db, credentials.username)
    if not user:
        raise FormException(status_code=400, detail="Username and password don't match")
    if not Hasher.verify_password(credentials.password, user.password):
        raise FormException(status_code=400, detail="Username and password don't match")
        
    access_token = Token.create_access_token(data={'sub': credentials.username})
    response.set_cookie(key="access_token",value=f"Bearer {access_token}", httponly=True)
    
    return {
        'access_token' : access_token,
        'token_type': 'bearer'
        }
    
@router.post('/login')
async def login_submit(
    request: Request, 
    login_form: schemas.UserLogin = Depends(schemas.UserLogin.as_form), 
    db: Session = Depends(get_db)
    ):
    response = RedirectResponse('../', status_code=status.HTTP_302_FOUND)
    await token(response=response, credentials=login_form, db=db)
    return response

@router.get('/logout')
async def logout(response: Response):
    response = RedirectResponse('../../phone_book/?alert=success&mess=Successfully LogOut', status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response