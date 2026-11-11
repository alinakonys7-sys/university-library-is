from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from app.database.db import init_db, get_session
from app.database.models import Author, Category
from app.routers.books import router as books_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Университет электрондық кітапханасы", lifespan=lifespan)
app.include_router(books_router)

@app.get("/")
def home():
    return {"message": "Электрондық кітапхана API жұмыс істеп тұр"}

@app.get("/categories", tags=["Анықтамалықтар"])
def categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()

@app.get("/authors", tags=["Анықтамалықтар"])
def authors(session: Session = Depends(get_session)):
    return session.exec(select(Author)).all()
