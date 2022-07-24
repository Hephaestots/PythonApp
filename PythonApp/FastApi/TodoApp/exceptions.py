from fastapi import HTTPException, status
from sqlalchemy import exc


def http_not_found_exception(name: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f'{name} not found')


def sqlalchemy_exception(error: exc.SQLAlchemyError) -> HTTPException:
    return HTTPException(status_code=int(error.code) if error.code else 412, detail='error')


def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return credentials_exception


def get_token_exception():
    token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return token_exception
