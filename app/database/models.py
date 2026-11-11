from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    books: list["Book"] = Relationship(back_populates="category")

class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = Field(index=True)
    books: list["Book"] = Relationship(back_populates="author")

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    publication_year: int = Field(ge=1450, le=2100)
    copies: int = Field(default=1, ge=0)
    category_id: int = Field(foreign_key="category.id")
    author_id: int = Field(foreign_key="author.id")
    category: Optional[Category] = Relationship(back_populates="books")
    author: Optional[Author] = Relationship(back_populates="books")

class BookCreate(SQLModel):
    title: str = Field(min_length=1)
    publication_year: int = Field(ge=1450, le=2100)
    copies: int = Field(ge=0)
    category_id: int
    author_id: int

    @field_validator("title")
    @classmethod
    def nonblank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Кітап атауы бос болмауы тиіс")
        return value

class BookUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1)
    publication_year: Optional[int] = Field(default=None, ge=1450, le=2100)
    copies: Optional[int] = Field(default=None, ge=0)
    category_id: Optional[int] = None
    author_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def nonblank(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError("Кітап атауы бос болмауы тиіс")
        return value.strip() if value is not None else None

class BookRead(SQLModel):
    id: int
    title: str
    publication_year: int
    copies: int
    category_id: int
    author_id: int
