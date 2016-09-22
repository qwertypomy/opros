#from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64),unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    api_key = db.Column(db.String(64), unique=True, index=True)
    polls = db.relationship('Poll', backref='user',
                                lazy='dynamic')


class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    questions = db.relationship('Question', backref='poll',
                                lazy='dynamic')


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    unswers = db.relationship('Unswer', backref='question',
                                lazy='dynamic')


class Unswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))