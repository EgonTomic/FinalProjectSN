import os
from sqla_wrapper import SQLAlchemy

db_url = os.getenv("DATABASE_URL", "sqlite:///db.sqlite")
db = SQLAlchemy(db_url)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    session_token = db.Column(db.String)
    country = db.Column(db.String)
    deleted = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, unique=False)
    authors_country = db.Column(db.String)
    message = db.Column(db.String, unique=False)