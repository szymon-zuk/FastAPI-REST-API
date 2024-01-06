from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=6)
    published_date: int = Field(gte=0, lt=2024)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "A new book",
                "author": "Szymson",
                "description": "New description",
                "rating": 5,
                "published_date": 2012
            }
        }


BOOKS = [
    Book(
        id=1,
        title="Computer Science Pro",
        author="Szymson",
        description="very nois book",
        rating=5,
        published_date=2012
    ),
    Book(
        id=2,
        title="Wiedźmin",
        author="Sapkowski",
        description="very nois book",
        rating=5,
        published_date=2016
    ),
    Book(
        id=3, title="DupaDupa", author="Szymson", description="very nois book", rating=4, published_date=2018
    ),
    Book(id=4, title="Potop", author="Sienkiewicz", description="słabe", rating=3, published_date=2024),
]


@app.get("/books")
async def read_all_books():
    return BOOKS


@app.get("/books/{book_id}/")
async def read_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book


@app.get("/books/")
async def read_book_by_rating(rating: int):
    books_to_return = []
    for book in BOOKS:
        if book.rating == rating:
            books_to_return.append(book)
    return books_to_return


@app.put("/books/update_book")
async def update_book(book: BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book


@app.post("/books/create_book")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            break


@app.get("/books/filter_by_date/{published_date}")
async def filter_books_by_date(published_date: int):
    books_to_return = []
    for i in range(len(BOOKS)):
        if BOOKS[i].published_date == published_date:
            books_to_return.append(BOOKS[i])
    return books_to_return
