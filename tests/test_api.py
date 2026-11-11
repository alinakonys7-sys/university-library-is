import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database.db import get_session
from app.database.models import Category, Author

@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(Category(id=1, name="Бағдарламалау"))
        session.add(Author(id=1, full_name="Тест автор"))
        session.commit()
    def override_session():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()

def payload(**changes):
    data = {"title": "Python негіздері", "publication_year": 2024, "copies": 5, "category_id": 1, "author_id": 1}
    data.update(changes)
    return data

def test_get_books(client):
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == []

def test_post_book(client):
    response = client.post("/books", json=payload())
    assert response.status_code == 201
    assert response.json()["title"] == "Python негіздері"

def test_filter_and_patch(client):
    created = client.post("/books", json=payload()).json()
    client.post("/books", json=payload(title="Java негіздері"))
    response = client.get("/books", params={"search": "python"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    updated = client.patch(f"/books/{created['id']}", json={"copies": 12})
    assert updated.status_code == 200
    assert updated.json()["copies"] == 12
    assert updated.json()["title"] == "Python негіздері"

def test_delete_and_missing(client):
    created = client.post("/books", json=payload()).json()
    response = client.delete(f"/books/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/books/{created['id']}").status_code == 404
    assert client.patch(f"/books/{created['id']}", json={"copies": 2}).status_code == 404

def test_invalid_input(client):
    assert client.post("/books", json=payload(copies=-1)).status_code == 422
    assert client.post("/books", json=payload(category_id=999)).status_code == 422
