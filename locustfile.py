"""Read-only load testing of local library API (does not mutate data)."""
from locust import HttpUser, task, between

class LibraryUser(HttpUser):
    wait_time = between(1, 2)

    @task(4)
    def list_books(self):
        self.client.get('/books', name='GET /books')

    @task(2)
    def search_books(self):
        self.client.get('/books?search=Python', name='GET /books?search')

    @task(1)
    def categories(self):
        self.client.get('/categories', name='GET /categories')
