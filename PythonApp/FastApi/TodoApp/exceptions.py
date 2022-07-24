from fastapi import HTTPException
from sqlalchemy import exc


def http_exception() -> HTTPException:
    return HTTPException(status_code=404, detail='Todo not found')


def sqlalchemy_exception(error: exc.SQLAlchemyError) -> HTTPException:
    return HTTPException(status_code=int(error.code) if error.code else 412, detail='error')
