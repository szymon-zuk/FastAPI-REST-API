from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette.responses import JSONResponse
from starlette import status

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
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gte=0, lt=2024)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "A new book",
                "author": "Szymson",
                "description": "New description",
                "rating": 5,
                "published_date": 2012,
            }
        }


BOOKS = [
    Book(
        id=1,
        title="Computer Science Pro",
        author="Szymson",
        description="very nois book",
        rating=5,
        published_date=2012,
    ),
    Book(
        id=2,
        title="Wiedźmin",
        author="Sapkowski",
        description="very nois book",
        rating=5,
        published_date=2016,
    ),
    Book(
        id=3,
        title="DupaDupa",
        author="Szymson",
        description="very nois book",
        rating=4,
        published_date=2018,
    ),
    Book(
        id=4,
        title="Potop",
        author="Sienkiewicz",
        description="słabe",
        rating=3,
        published_date=2024,
    ),
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


@app.get("/books/filter_by_date/", status_code=status.HTTP_200_OK)
async def filter_books_by_date(published_date: int = Query(gt=0, lt=2024)):
    books_to_return = [book for book in BOOKS if book.published_date == published_date]
    return books_to_return


@app.get("/books/{book_id}/", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    book = next((book for book in BOOKS if book.id == book_id), None)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(rating: int = Query(gt=0, lt=6)):
    return [book for book in BOOKS if book.rating == rating]


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail="Book not found")


@app.post("/books/create_book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))


def find_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_index = next((i for i, book in enumerate(BOOKS) if book.id == book_id), None)
    if book_index is not None:
        BOOKS.pop(book_index)
    raise HTTPException(status_code=404, detail="Book not found")
