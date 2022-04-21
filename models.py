from datetime import datetime
from email.policy import default
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import func
from flask_login import UserMixin

db = SQLAlchemy()


def setup(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db


class Show(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    start_time = db.Column(db.DateTime(timezone=True), default=func.now())
    venue_id = db.Column(db.Integer(), db.ForeignKey(
        'venue.id'), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey(
        'user.id'), nullable=False)


class Venue(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    image_place = db.Column(db.String(100))
    name_place = db.Column(db.String(100))
    address_place = db.Column(db.String(100))
    has_show = db.Column(db.Boolean(), default=False)
    venue = db.relationship('Show', backref='venue')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(20), unique=True)
    password = db.Column(db.String())
    username = db.Column(db.String())
    position = db.Column(db.String())
    data_joined = db.Column(db.DateTime(), default=datetime.now())
    is_artist = db.Column(db.Boolean(), default=False)
    venue = db.relationship('Show', backref='user')
