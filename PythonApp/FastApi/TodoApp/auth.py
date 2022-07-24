from datetime import datetime, timedelta
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import exc
from sqlalchemy.orm import Session
from typing import Optional

from database import SessionLocal, alchemy_engine
from exceptions import sqlalchemy_exception, get_user_exception, get_token_exception
from responses import successful_response
import models

SECRET_KET = "3Fj1Xek1qM5vfQmMLyLIWXvBHPSSGHeI"
ALGORITHM = "HS256"


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=alchemy_engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")


app = FastAPI()


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# API Endpoints
@app.post("/create/user")
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)) -> models.Users:
    user_model = models.Users()
    user_model.email = create_user.email
    user_model.username = create_user.username
    user_model.first_name = create_user.first_name
    user_model.last_name = create_user.last_name

    hash_pw = get_password_hash(create_user.password)

    user_model.hashed_pw = hash_pw
    user_model.is_active = True

    try:
        db.add(user_model)
        db.commit()
    except exc.SQLAlchemyError as error:
        raise sqlalchemy_exception(error)
    return successful_response(201)


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user: Optional[models.Users] = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise get_token_exception()

    token_expires = timedelta(minutes=20)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)
    return {"token": token}


# Private Methods
def authenticate_user(username: str, password: str, db: Session):
    user: models.Users = db.query(models.Users)\
        .filter(models.Users.username == username)\
        .first()

    if not user:
        return None
    if not verify_password(password, user.hashed_pw):
        return None
    return user


def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KET, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KET, algorithm=ALGORITHM)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if not username or not user_id:
            raise get_user_exception()
        return {"username": username, "id": user_id}
    except JWTError as error:
        raise get_user_exception()


def get_password_hash(password) -> str:
    return bcrypt_context.hash(password)


def verify_password(pw: str, hash_pw: str) -> bool:
    return bcrypt_context.verify(pw, hash_pw)
