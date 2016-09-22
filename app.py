import os
from flask import Flask, jsonify, request, url_for
from flask_login import LoginManager, current_user, login_required
from models import db, User, Poll, Question, Unswer
from schemas import ma, user_schema, users_schema, poll_schema, \
										polls_schema, unswer_schema, unswers_schema, \
										question_schema, questions_schema


login_manager = LoginManager()


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
ma.init_app(app)
login_manager.init_app(app)


@app.route('/')
def hello():
    return jsonify({"message" : "Hello World!"})


@app.route("/profile")
@login_required
def user_profile():
    return user_schema.jsonify(current_user)    


@app.errorhandler(404)
def page_not_found(error):
    resp = jsonify({"error": "not found"})
    resp.status_code = 404
    return resp


@app.errorhandler(401)
def unauthorized(error):
    resp = jsonify({"error": "unauthorized"})
    resp.status_code = 401
    return resp


if __name__ == '__main__':
    app.run()