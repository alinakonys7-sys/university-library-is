from sqlmodel import Session, select
from app.database.db import engine, init_db
from app.database.models import Category, Author, Book

def seed():
    init_db()
    with Session(engine) as session:
        if session.exec(select(Category)).first():
            print("Деректер бұрын енгізілген; қайталанбайды")
            return
        categories = [Category(name=n) for n in ["Бағдарламалау", "Математика", "Желілер", "Деректер базасы"]]
        authors = [Author(full_name=n) for n in ["Роберт Мартин", "Эрик Маттес", "Эндрю Таненбаум", "Томас Кормен"]]
        session.add_all(categories + authors)
        session.flush()
        books = [
            Book(title="Clean Code", publication_year=2008, copies=5, category_id=categories[0].id, author_id=authors[0].id),
            Book(title="Python Crash Course", publication_year=2019, copies=4, category_id=categories[0].id, author_id=authors[1].id),
            Book(title="Computer Networks", publication_year=2010, copies=3, category_id=categories[2].id, author_id=authors[2].id),
            Book(title="Introduction to Algorithms", publication_year=2009, copies=6, category_id=categories[1].id, author_id=authors[3].id),
            Book(title="Programming Principles", publication_year=2020, copies=2, category_id=categories[0].id, author_id=authors[1].id),
        ]
        session.add_all(books)
        session.commit()
        print("Дайын: 4 категория, 4 автор, 5 кітап")

if __name__ == "__main__":
    seed()
