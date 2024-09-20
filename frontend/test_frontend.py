import pytest

from server import cowrywisebea_app
from dbmodel import db, User


@pytest.fixture
def client():
    with cowrywisebea_app.test_client() as client:
        with cowrywisebea_app.app_context():
            db.create_all()

        yield client
        
        with cowrywisebea_app.app_context():
            db.session.query(User).filter_by(email="test3account@test.com").delete()
            db.session.commit()

        db.session.remove()


def test_enroll_user(client):
    response = client.post(
        "/user/sign-up",
        json={
            'firstname': "Test 3",
            'lastname': "Account",
            'email': "test3account@test.com",
        },
    )
    
    assert response.status_code == 201


def test_list_books(client):
    response = client.get("/user/books")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)


def test_get_book_by_id(client):
    response = client.get("/user/books/5")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, dict)


def test_filter_books_by_category(client):
    response = client.get("/user/books/Fiction?category=Fiction")

    assert response.status_code == 200

    data = response.get_json()

    assert all(book.get("category") == "Fiction" for book in data)
