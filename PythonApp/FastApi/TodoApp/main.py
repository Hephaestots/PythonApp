from database import alchemy_engine, SessionLocal
from fastapi import Depends, FastAPI
from sqlalchemy import exc
from sqlalchemy.orm import Session
from typing import Dict

# Custom Modules
from dto import Todo
from exceptions import http_not_found_exception, sqlalchemy_exception
from responses import successful_response
import models

app = FastAPI()

models.Base.metadata.create_all(bind=alchemy_engine)


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
async def read_all(db: Session = Depends(get_db)) -> Dict[int, models.Todos]:
    return db.query(models.Todos).all()


@app.get("/todos/{todo_id}")
async def read_todo(todo_id: int, db: Session = Depends(get_db)) -> models.Todos:
    todo = db.query(models.Todos) \
        .filter(models.Todos.id == todo_id) \
        .first()

    if todo:
        return todo
    raise http_not_found_exception("Todo")


@app.post("/")
async def create_todo(todo: Todo, db: Session = Depends(get_db)) -> dict[str, str | int]:
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    try:
        db.add(todo_model)
        db.commit()
    except exc.SQLAlchemyError as error:
        raise sqlalchemy_exception(error)
    return successful_response(201)


@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, todo: Todo, db: Session = Depends(get_db)) -> dict[str, str | int]:
    old_todo: models.Todos = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .first()

    if not old_todo:
        raise http_not_found_exception("Todo")

    old_todo.title = todo.title
    old_todo.description = todo.description
    old_todo.priority = todo.priority
    old_todo.complete = todo.complete

    try:
        db.add(old_todo)
        db.commit()
    except exc.SQLAlchemyError as error:
        raise sqlalchemy_exception(error)
    return successful_response(200)


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)) -> dict[str, str | int]:
    old_todo: models.Todos = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .first()

    if not old_todo:
        raise http_not_found_exception("Todo")

    try:
        db.query(models.Todos)\
            .filter(models.Todos.id == todo_id)\
            .delete()
        db.commit()
    except exc.SQLAlchemyError as error:
        raise sqlalchemy_exception(error)
    return successful_response(200)
