from flask_marshmallow import Marshmallow
from models import User, Poll, Question, Unswer

ma = Marshmallow()


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User


class PollSchema(ma.ModelSchema):
    class Meta:
    		model = Poll 
    		exclude = ('questions',)


class QuestionSchema(ma.ModelSchema):
    class Meta:
        model = Question


class UnswerSchema(ma.ModelSchema):
    class Meta:
        model = Unswer

user_schema = UserSchema()
users_schema = UserSchema(many=True)

poll_schema = PollSchema()
polls_schema = PollSchema(many=True)

question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)

unswer_schema = UnswerSchema()
unswers_schema = UnswerSchema(many=True)