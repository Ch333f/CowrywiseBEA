from flask_restx import Resource, Namespace, fields
from flask import request, jsonify, make_response
import requests

from datetime import datetime, timedelta, timezone

from dbmodel import db, User, Book, BooksBorrowed


user = Namespace(
    name="User",
    description="User namespace",
    path="/user",
)

sign_up_form = user.model(
    "Sign up Form",
    {
        'firstname': fields.String(required=True),
        'lastname': fields.String(required=True),
        'email': fields.String(required=True),
    },
)
book_model = user.model(
    "Book",
    {
        'id': fields.Integer(),
        'title': fields.String(required=True),
        'author': fields.String(required=True),
        'publisher': fields.String(required=True),
        'category': fields.String(required=True),
        'available': fields.Boolean,
        'date_added': fields.Date,
    },
)
book_form = user.inherit(
    "Book Form",
    book_model,
    {'user_privilege': fields.String(required=True)}
)
borrow_book_form = user.model(
    "Borrow Book Form",
    {
        'borrower': fields.String(required=True),
        'return_period': fields.Integer(),
    },
)

admin_service = "http://127.0.0.1:5001/admin"


@user.route(
    "/sign-up",
    methods=["POST"],
)
class SignUp(Resource):
    @user.expect(
        sign_up_form,
        validate=True,
    )
    def post(self):
        """
        Enroll users into the library using their email, firstname and lastname.
        """
        form_data = request.json
        user = User(
            firstname=form_data.get("firstname"),
            lastname=form_data.get("lastname"),
            email=form_data.get("email"),
        )

        db.session.add(user)
        db.session.commit()

        # notify admin service
        requests.post(
            f'{admin_service}/sign-up',
            json=form_data,
        )

        return make_response(
            jsonify({'message': "User enrolled successfully"}), 201
        )


@user.route(
    "/books",
    methods=["GET", "POST"],
)
class Books(Resource):
    @user.marshal_list_with(book_model)
    def get(self):
        """
        List all available books
        """
        return Book.query.filter_by(available=True).all()


    @user.expect(
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

            return make_response(
                jsonify({'message': "Book added successfully"}), 201
            )

        return make_response(
            jsonify({'message': "You don't have access to this resource"}), 401
        )


@user.route(
    "/books/<int:id>",
    methods=["GET", "POST"],
)
class Book_(Resource):
    @user.marshal_list_with(book_model)
    def get(self, id):
        """
        Get a single book by its ID
        """
        return Book.query.get_or_404(id)


    @user.expect(
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

        # notify admin service
        requests.post(
            f'{admin_service}/books/{book.id}',
            json=form_data,
        )

        return make_response(
            jsonify({'message': "Book borrowed successfully"}), 200
        )


@user.route(
    "/books/<string:keyword>",
    methods=["GET"],
)
class FilterBooks(Resource):
    @user.marshal_list_with(book_model)
    def get(self, keyword):
        """
        Filter books by publishers eg Wiley, Apress, Manning and by category eg fiction, technology, science
        """
        return (
            Book.query
                .filter(
                    (Book.publisher == keyword) | (Book.category == keyword)
                )
                .all()
        )
