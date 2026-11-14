"""Lab 8: isolated API/SQLite integration, validation and security checks."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database.db import get_session
from app.database.models import Category, Author, Book

@pytest.fixture
def env():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(Category(id=1, name="IT"))
        db.add(Author(id=1, full_name="Test author"))
        db.commit()
    def session_override():
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_session] = session_override
    try:
        with TestClient(app) as client:
            yield client, engine
    finally:
        app.dependency_overrides.clear()
        engine.dispose()

def book(**kwargs):
    data = dict(title="Python", publication_year=2024, copies=2, category_id=1, author_id=1)
    data.update(kwargs)
    return data

def test_integrated_create_read(env):
    c, db = env
    r = c.post('/books', json=book())
    assert r.status_code == 201
    with Session(db) as s:
        assert s.get(Book, r.json()['id']).title == 'Python'

def test_integrated_patch_db(env):
    c, db = env
    bid = c.post('/books', json=book()) .json()['id']
    assert c.patch(f'/books/{bid}', json={'copies': 8}).status_code == 200
    with Session(db) as s:
        assert s.get(Book, bid).copies == 8

def test_integrated_delete_db(env):
    c, db = env
    bid = c.post('/books', json=book()).json()['id']
    assert c.delete(f'/books/{bid}').status_code == 204
    with Session(db) as s:
        assert s.get(Book, bid) is None

def test_integrated_filter(env):
    c, _ = env
    c.post('/books', json=book(title='Python'))
    c.post('/books', json=book(title='Go'))
    r = c.get('/books', params={'search':'py'})
    assert r.status_code == 200 and len(r.json()) == 1

def test_integrated_reference_data(env):
    c, _ = env
    assert c.get('/categories').json()[0]['name'] == 'IT'
    assert c.get('/authors').json()[0]['full_name'] == 'Test author'

def test_security_empty_title(env):
    c, _ = env
    assert c.post('/books', json=book(title='  ')).status_code == 422

def test_security_negative_copies(env):
    c, _ = env
    assert c.post('/books', json=book(copies=-1)).status_code == 422

def test_security_unknown_relation(env):
    c, _ = env
    assert c.post('/books', json=book(author_id=999)).status_code == 422

def test_security_invalid_json(env):
    c, _ = env
    r = c.post('/books', content='{broken', headers={'content-type':'application/json'})
    assert r.status_code == 422

def test_security_missing_book(env):
    c, _ = env
    assert c.get('/books/99999').status_code == 404

def test_boundary_zero_copies(env):
    c, _ = env
    assert c.post('/books', json=book(copies=0)).status_code == 201

def test_boundary_min_year(env):
    c, _ = env
    assert c.post('/books', json=book(publication_year=1450)).status_code == 201

def test_boundary_year_too_early(env):
    c, _ = env
    assert c.post('/books', json=book(publication_year=1449)).status_code == 422

def test_transaction_rollback(env):
    _, engine = env
    with pytest.raises(RuntimeError):
        with Session(engine) as s:
            s.add(Book(title='Rollback test', publication_year=2024, copies=1, category_id=1, author_id=1))
            s.flush()
            s.rollback()
            raise RuntimeError('Intentional rollback check')
    with Session(engine) as s:
        assert s.exec(select(Book).where(Book.title == 'Rollback test')).first() is None

def test_no_auth_module_documented(env):
    # Current application has no authentication/roles. This is a GAP, not a pass of access control.
    c, _ = env
    assert c.get('/books').status_code == 200
