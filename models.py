from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

answer_user = db.Table('answer_user', db.Model.metadata,
    db.Column('answer_id', db.Integer, db.ForeignKey('answer.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)
poll_user = db.Table('poll_user', db.Model.metadata,
    db.Column('poll_id', db.Integer, db.ForeignKey('poll.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256),unique=True, nullable=False)
    user_name = db.Column(db.String(32), nullable=False)
    api_key = db.Column(db.String(64), unique=True, index=True)
    polls = db.relationship('Poll', backref='user',
                            lazy='dynamic')

    def __init__(self, email, user_name):
        self.email = email
        self.user_name = user_name

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
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
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    questions = db.relationship('Question', backref='poll',
                                lazy='dynamic')
    viewers = db.relationship("User", secondary=poll_user)
    @property
    def url(self):
        return url_for("get_poll", id=self.id)

    def add_viewer(self, viewer):
        self.viewers.append(viewer)
        return self



class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256), nullable=False)
    def_answer = db.Column(db.Boolean)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    answers = db.relationship('Answer', backref='question',
                              lazy='dynamic')

    @property
    def url(self):
        return url_for("get_question", id=self.id, p_id = self.poll_id)


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    user = db.relationship("User", secondary=answer_user)

    @property
    def get_poll_id(self):
        question = Question.query.get_or_404(self.question_id)
        return question.poll_id

    @property
    def url(self):
        return url_for("get_answer", id=self.id, p_id=self.get_poll_id, q_id = self.question_id)

    def reply(self, user):
        self.user.append(user)
        return self

    def cancel_reply(self, user):
        self.user.remove(user)
        return self

