import pytest

from server import cowrywisebea_app
from dbmodel import db, Book


@pytest.fixture
def client():
    with cowrywisebea_app.test_client() as client:
        with cowrywisebea_app.app_context():
            db.create_all()

        yield client
        
        with cowrywisebea_app.app_context():
            db.session.query(Book).filter_by(title="Dune").delete()
            db.session.commit()

        db.session.remove()


def test_add_book(client):
    response = client.post(
        "/admin/books",
        json={
            'user_privilege': "Admin",
            'title': "Dune",
            'author': "Frank Herbert",
            'publisher': "Chilton Books",
            'category': "Science Fiction",
        },
    )

    assert response.status_code == 201


def test_remove_book(client):
    add_response = client.post(
        "/admin/books",
        json={
            'user_privilege': "Admin",
            'title': "Dune",
            'author': "Frank Herbert",
            'publisher': "Chilton Books",
            'category': "Science Fiction",
        },
    )

    assert add_response.status_code == 201

    delete_response = client.delete(f'/admin/books/{10}')

    assert delete_response.status_code == 200
