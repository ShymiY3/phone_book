from fastapi import Depends, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from . import models
from ..exceptions import FormException
from .utils import OAuth2PasswordBearerWithCookie
from ..config import settings
from ..database import get_db

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token", scheme_name='JWT')

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user):
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = FormException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(username=username, db=db)
    if user is None:
        raise credentials_exception
    return user