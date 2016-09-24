from flask_marshmallow import Marshmallow
from models import User, Poll, Question, Answer

ma = Marshmallow()


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        exclude = ('password', 'api_key')


class PollSchema(ma.ModelSchema):
    class Meta:
        model = Poll

class QuestionSchema(ma.ModelSchema):
    class Meta:
        model = Question


class AnswerSchema(ma.ModelSchema):
    class Meta:
        model = Answer

user_schema = UserSchema()
users_schema = UserSchema(many=True)

poll_schema = PollSchema()
polls_schema = PollSchema(many=True)

question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)

answer_schema = AnswerSchema()
answers_schema = AnswerSchema(many=True)