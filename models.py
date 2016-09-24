from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(16),unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    user_name = db.Column(db.String(32), nullable=False)
    api_key = db.Column(db.String(64), unique=True, index=True)
    polls = db.relationship('Poll', backref='user',
                            lazy='dynamic')

    def __init__(self, email, password, user_name):
        self.email = email
        self.password = password #bcrypt.generate_password_hash(password)
        self.user_name = user_name

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<email {}'.format(self.email)

    @property
    def url(self):
        return url_for("get_user", id=self.id)


class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    questions = db.relationship('Question', backref='poll',
                                lazy='dynamic')

    @property
    def url(self):
        return url_for("get_poll", id=self.id)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    unswers = db.relationship('Unswer', backref='question',
                              lazy='dynamic')

    @property
    def url(self):
        return url_for("get_question", id=self.id, p_id = self.poll_id)

class Unswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
