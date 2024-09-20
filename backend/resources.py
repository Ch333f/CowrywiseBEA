from flask_restx import Resource, Namespace, fields
from flask import request, jsonify, make_response
import requests

from datetime import datetime, timedelta, timezone

from dbmodel import db, User, Book, BooksBorrowed


admin = Namespace(
    name="Admin",
    description="Admin namespace",
    path="/admin",
)

sign_up_form = admin.model(
    "Sign up Form",
    {
        'firstname': fields.String(required=True),
        'lastname': fields.String(required=True),
        'email': fields.String(required=True),
    },
)
book_form = admin.model(
    "Book Form",
    {
        'user_privilege': fields.String(required=True),
        'title': fields.String(required=True),
        'author': fields.String(required=True),
        'publisher': fields.String(required=True),
        'category': fields.String(required=True),
        'available': fields.Boolean,
    }
)
borrow_book_form = admin.model(
    "Borrow Book Form",
    {
        'borrower': fields.String(required=True),
        'return_period': fields.Integer(),
    },
)

user_service = "http://127.0.0.1:5000/user"


@admin.route(
    "/sign-up",
    methods=["POST"],
)
class SignUp(Resource):
    @admin.expect(
        sign_up_form,
        validate=True,
    )
    def post(self):
        """
        Enroll users into the library using their firstname, lastname and email
        """
        form_data = request.json
        user = User(
            firstname=form_data.get("firstname"),
            lastname=form_data.get("lastname"),
            email=form_data.get("email"),
        )

        db.session.add(user)
        db.session.commit()

        return make_response(
            jsonify({'message': "User enrolled successfully"}), 201
        )


@admin.route(
    "/users",
    methods=["GET"],
)
class User_(Resource):
    def get(self):
        """
        Fetch/List users enrolled in the library and Fetch/List users and the books they have borrowed
        """
        users = User.query.all()

        return [
            {
                'id': user.id,
                'firstname': user.firstname,
                'lastname': user.lastname,
                'email': user.email,
                'date_created': user.date_created.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                'books_borrowed': [
                    {
                        'id': book_borrowed.id,
                        'book_id': book_borrowed.book_id,
                        'return_date': (
                            book_borrowed.return_date
                                .strftime("%Y-%m-%dT%H:%M:%S.%f")
                        ),
                        'date_borrowed': (
                            book_borrowed.date_borrowed
                                .strftime("%Y-%m-%dT%H:%M:%S.%f")
                        ),
                    }
                    for book_borrowed in user.books_borrowed
                ],
            }
            for user in users
        ]


@admin.route(
    "/books",
    methods=["POST", "GET"],
)
class Books(Resource):
    @admin.expect(
        book_form,
        validate=True,
    )
    def post(self):
        """
        Add new books to the catalogue
        """
        form_data = request.json

        if form_data.get("user_privilege") == "Admin":
            book = Book(
                title=form_data.get("title"),
                author=form_data.get("author"),
                publisher=form_data.get("publisher"),
                category=form_data.get("category"),
            )

            db.session.add(book)
            db.session.commit()

            # notify user service
            requests.post(
                f'{user_service}/books',
                json=form_data,
            )

            return make_response(
                jsonify({'message': "Book added successfully"}), 201
            )

        return make_response(
            jsonify({'message': "You don't have access to this resource"}), 401
        )


    def get(self):
        """
        Fetch/List the books that are not available for borrowing (showing the day it will be available)
        """
        books = Book.query.filter_by(available=False).all()

        return [
            {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'publisher': book.publisher,
                'category': book.category,
                'available': book.available,
                'date_added': book.date_added.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                'borrowed': [
                    {
                        'id': borrowed_book.id,
                        'user_id': borrowed_book.user_id,
                        'return_date': (
                            borrowed_book.return_date
                                .strftime("%Y-%m-%dT%H:%M:%S.%f")
                        ),
                        'date_borrowed': (
                            borrowed_book.date_borrowed
                                .strftime("%Y-%m-%dT%H:%M:%S.%f")
                        ),
                    }
                    for borrowed_book in book.borrowed
                ],
            }
            for book in books
        ]


@admin.route(
    "/books/<int:id>",
    methods=["DELETE", "POST"],
)
class Book_(Resource):
    def delete(self, id):
        """
        Remove a book from the catalogue
        """
        book = Book.query.get_or_404(id)

        db.session.delete(book)
        db.session.commit()

        return make_response(
            jsonify({'message': "Book removed from catalogue successfully."}),
            200,
        )


    @admin.expect(
        borrow_book_form,
        validate=True,
    )
    def post(self, id):
        """
        Borrow books by id (specify how long you want it for in days)
        """
        form_data = request.json
        book = Book.query.get_or_404(id)

        if not book.available:
            return make_response(
                jsonify({'message': "Book not available"}), 400
            )

        borrowed_book = BooksBorrowed(
            book_id=book.id,
            user_id=form_data.get("borrower"),
            return_date= (
                datetime.now(timezone.utc)
                + timedelta(days=int(form_data.get("return_period", 7)))  # return_period default to 7 days
            ),
        )

        book.available = False

        db.session.add(borrowed_book)
        db.session.commit()

        return make_response(
            jsonify({'message': "Book borrowed successfully"}), 200
        )
