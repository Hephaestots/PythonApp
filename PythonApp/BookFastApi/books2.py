from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional


class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    description: Optional[str] = Field(title="Description of book.",
                                       min_length=1,
                                       max_length=250)
    author: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=101, title="Rating of book from 0 to 100.")

    # Configuration of the default values for the BaseModel.
    class Config:
        schema_extra = {
            "example": {
                "id": uuid4(),
                "title": "Software Engineering 101",
                "description": "Basics of software engineering.",
                "author": "Hephaestots",
                "rating": 99
            }
        }


app = FastAPI()


BOOKS = []


@app.get("/")
async def read_all_books(books_to_return: Optional[int] = None) -> list[Book]:
    if len(BOOKS) < 1:
        create_books_no_api()

    if books_to_return and len(BOOKS) >= books_to_return > 0:
        i = 1
        new_books = []
        while i <= books_to_return:
            new_books.append(BOOKS[i - 1])
            i += 1
        return new_books
    return BOOKS


@app.get("/books/{book_id}")
async def read_book(book_id: UUID) -> Book:
    matched_books = [book for book in BOOKS if book.id == book_id]
    if not matched_books:
        raise HTTPException(status_code=401, detail="This book doesn't exist.")
    return matched_books.pop(0)


@app.post("/")
async def create_book(book: Book) -> Book:
    BOOKS.append(book)
    return book


@app.put("/books/{book_id}")
async def update_book(book_id: UUID, book: Book) -> Book:
    matched_books = [book for book in BOOKS if book.id == book_id]
    if not matched_books:
        raise HTTPException(status_code=401, detail="This book doesn't exist.")

    index = BOOKS.index(matched_books.pop(0))
    book.id = book_id
    BOOKS[index] = book
    return book


@app.delete("/books/{book_id}")
async def delete_book(book_id: UUID) -> str:
    matched_books = [book for book in BOOKS if book.id == book_id]
    if not matched_books:
        raise HTTPException(status_code=401, detail="This book doesn't exist.")

    match = matched_books.pop(0)
    index = BOOKS.index(match)
    del BOOKS[index]
    return f"Book {book_id} has been deleted."


# Helper methods
def create_books_no_api() -> None:
    book_1 = Book(id=uuid4(),
                  title="Title of book_1",
                  author="Author of book_1",
                  description="Description of book_1",
                  rating=55)
    book_2 = Book(id=uuid4(),
                  title="Title of book_2",
                  author="Author of book_2",
                  rating=85)
    book_3 = Book(id=uuid4(),
                  title="Title of book_3",
                  author="Author of book_3",
                  rating=95)
    book_4 = Book(id=uuid4(),
                  title="Title of book_4",
                  author="Author of book_4",
                  rating=49)
    BOOKS.append(book_1)
    BOOKS.append(book_2)
    BOOKS.append(book_3)
    BOOKS.append(book_4)
