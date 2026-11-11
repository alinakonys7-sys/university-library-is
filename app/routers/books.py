from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from app.database.db import get_session
from app.database.models import Book, BookCreate, BookRead, BookUpdate, Category, Author

router = APIRouter(prefix="/books", tags=["Кітаптар"])

def validate_relations(session: Session, category_id: int, author_id: int):
    if session.get(Category, category_id) is None:
        raise HTTPException(422, "Мұндай категория жоқ")
    if session.get(Author, author_id) is None:
        raise HTTPException(422, "Мұндай автор жоқ")

@router.get("", response_model=list[BookRead])
def list_books(search: Optional[str] = None, min_year: Optional[int] = None,
               max_year: Optional[int] = None, category_id: Optional[int] = None,
               min_copies: Optional[int] = Query(default=None, ge=0),
               max_copies: Optional[int] = Query(default=None, ge=0),
               session: Session = Depends(get_session)):
    if min_year is not None and max_year is not None and min_year > max_year:
        raise HTTPException(422, "min_year max_year-дан аспауы тиіс")
    if min_copies is not None and max_copies is not None and min_copies > max_copies:
        raise HTTPException(422, "min_copies max_copies-тан аспауы тиіс")
    stmt = select(Book)
    if search:
        stmt = stmt.where(Book.title.icontains(search))
    if min_year is not None:
        stmt = stmt.where(Book.publication_year >= min_year)
    if max_year is not None:
        stmt = stmt.where(Book.publication_year <= max_year)
    if category_id is not None:
        stmt = stmt.where(Book.category_id == category_id)
    if min_copies is not None:
        stmt = stmt.where(Book.copies >= min_copies)
    if max_copies is not None:
        stmt = stmt.where(Book.copies <= max_copies)
    return session.exec(stmt).all()

@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(404, "Кітап табылмады")
    return book

@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, session: Session = Depends(get_session)):
    validate_relations(session, payload.category_id, payload.author_id)
    book = Book.model_validate(payload)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@router.patch("/{book_id}", response_model=BookRead)
def update_book(book_id: int, payload: BookUpdate, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(404, "Кітап табылмады")
    changes = payload.model_dump(exclude_unset=True)
    if any(v is None for v in changes.values()):
        raise HTTPException(422, "Өрісті null мәніне өзгертуге болмайды")
    validate_relations(session, changes.get("category_id", book.category_id), changes.get("author_id", book.author_id))
    book.sqlmodel_update(changes)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(404, "Кітап табылмады")
    session.delete(book)
    session.commit()
    return None
