from fastapi import FastAPI, Header, HTTPException, Request, status
from starlette.responses import JSONResponse
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional


class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    description: Optional[str] = Field(None,
                                       title="Description of book",
                                       min_length=1,
                                       max_length=250)
    author: str = Field(min_length=1,
                        max_length=100)
    rating: int = Field(gt=-1,
                        lt=101,
                        title="Rating of book from 0 to 100.")

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


class BookNoRating(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    description: Optional[str] = Field(None,
                                       min_length=1,
                                       max_length=250,
                                       title="Description of book")
    author: str = Field(min_length=1,
                        max_length=100)


class NegativeNumberException(Exception):
    def __init__(self, books_to_return):
        self.books_to_return = books_to_return


class InvalidUserException(Exception):
    def __init__(self, username, password):
        self.username = username
        self.password = password


app = FastAPI()


BOOKS = []


# Exception handlers
@app.exception_handler(NegativeNumberException)
async def negative_number_exception_handler(request: Request,
                                            exception: NegativeNumberException):
    return JSONResponse(status_code=418,
                        content={"message": f"Hey, why do you want {exception.books_to_return} "
                                            f"books? You need to read more!"})


@app.exception_handler(InvalidUserException)
async def invalid_user_exception_handler(request: Request,
                                         exception: InvalidUserException):
    return JSONResponse(status_code=401,
                        content={"message": "Invalid User"})


# API Endpoints
@app.post('/books/login')
async def book_login(book_id: UUID, username: Optional[str] = Header(None), password: Optional[str] = Header(None)):
    if not username.__eq__("FastAPIUser") or not password.__eq__("test1234!"):
        raise InvalidUserException(username, password)
    return find_specific_book(book_id)


@app.get("/header")
async def read_header(random_header: Optional[str] = Header(None)):
    return {"Random-Header": random_header}


@app.get("/")
async def read_all_books(books_to_return: Optional[int] = None) -> list[Book]:
    if books_to_return and books_to_return < 0:
        raise NegativeNumberException(books_to_return)

    if len(BOOKS) < 1:
        create_books_no_api()

    if books_to_return and len(BOOKS) >= books_to_return > 0:
        return BOOKS[0:books_to_return]
    return BOOKS


@app.get("/books/{book_id}")
async def read_book(book_id: UUID) -> Book:
    return find_specific_book(book_id)


@app.get("/books/rating/{book_id}", response_model=BookNoRating)
async def read_book_no_rating(book_id: UUID) -> Book:
    return find_specific_book(book_id)


@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(book: Book) -> Book:
    BOOKS.append(book)
    return book


@app.put("/books/{book_id}")
async def update_book(book_id: UUID, book: Book) -> Book:
    index = BOOKS.index(find_specific_book(book_id))
    book.id = book_id
    BOOKS[index] = book
    return book


@app.delete("/books/{book_id}")
async def delete_book(book_id: UUID) -> str:
    match = find_specific_book(book_id)
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


def find_specific_book(book_id: UUID) -> Book:
    matched_books = [book for book in BOOKS if book.id == book_id]
    if not matched_books:
        raise item_cannot_be_found_exception()
    return matched_books.pop(0)


def item_cannot_be_found_exception() -> HTTPException:
    return HTTPException(status_code=404,
                         detail="Book Not Found",
                         headers={
                             "X-Header-Error": "Nothing to be seen at the UUID"
                         })
