from flask_sqlalchemy import SQLAlchemy

from datetime import datetime, timezone


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True,
    )
    firstname = db.Column(
        db.String(50),
        nullable=False,
    )
    lastname = db.Column(
        db.String(50),
        nullable=False,
    )
    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
    )
    date_created = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    books_borrowed = db.relationship(
        "BooksBorrowed",
        foreign_keys="BooksBorrowed.user_id",
        backref="_books_borrowed",
        lazy="select",
    )


class Book(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True,
    )
    title = db.Column(
        db.String(200),
        nullable=False,
    )
    author = db.Column(
        db.String(100),
        nullable=False,
    )
    publisher = db.Column(
        db.String(100),
        nullable=False,
    )
    category = db.Column(
        db.String(50),
        nullable=False,
    )
    available = db.Column(
        db.Boolean,
        default=True,
    )
    date_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    borrowed = db.relationship(
        "BooksBorrowed",
        foreign_keys="BooksBorrowed.book_id",
        backref="_borrowed",
        lazy="select",
    )


    def __repr__(self):
        return f'<Book {self.title}>'


class BooksBorrowed(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True,
    )
    book_id = db.Column(
        db.Integer,
        db.ForeignKey("book.id"),
        nullable=False,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
    )
    return_date = db.Column(db.Date)
    date_borrowed = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
    )
