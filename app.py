import os
from flask import Flask, jsonify, request, url_for, redirect, session
from flask_login import LoginManager, current_user, login_required, \
    login_user, logout_user
from models import db, User, Poll, Question, Answer
from schemas import ma, user_schema, users_schema, poll_schema, \
    polls_schema, answer_schema, answers_schema, \
    question_schema, questions_schema


login_manager = LoginManager()


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
ma.init_app(app)
login_manager.init_app(app)



@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()

@login_manager.request_loader
def load_user_from_request(request):

    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None


@app.route("/")
def index():
    return redirect(url_for('polls'))


@app.route("/users")
def users():
    all_users = User.query.all()
    return users_schema.jsonify(all_users)


@app.route("/users/<int:id>")
def get_user(id):
    if current_user.is_authenticated and current_user.id == id:
        return redirect(url_for('profile'))
    user = User.query.get_or_404(id)
    return user_schema.jsonify(user)


@app.route("/profile")
@login_required
def profile():
    return user_schema.jsonify(current_user)


@app.route("/profile", methods=['PUT'])
@login_required
def change_user_name():
    if request.form['user_name']:
        current_user.user_name = request.form['user_name']
        db.session.commit()
        resp = jsonify({'message': 'user name successfuly changed'})
        resp.status_code = 201
        return resp
    resp = jsonify({'error': 'Invalid user name'})
    resp.status_code = 400
    return resp


@app.route("/registration", methods=['POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    try:
        rf = request.form
        user = User(rf['email'], rf['password'], rf['user_name'])
        db.session.add(user)
        db.session.commit()

        user = User.query.filter_by(email=rf['email']).first()
        login_user(user)

        resp = jsonify({"message": "registration successful"})
        resp.status_code = 201
        resp.headers["Location"] = user.url
        return resp
    except:
        resp = jsonify({'error':'Invalid input'})
        resp.status_code = 400
        return resp


@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    rf = request.form
    user = User.query.filter_by(email=rf['email']).first()
    if user and user.password == rf['password']:
        login_user(user)
        resp = jsonify({'message': 'successfully logged in'})
        resp.status_code = 201
        return resp #redirect(url_for('polls'))
    resp = jsonify({'error':'Wrong email or password'})
    resp.status_code = 400
    return resp


@app.route("/logout")
@login_required
def logout():
    logout_user()
    resp = jsonify({'message': 'successfully logged out'})
    resp.status_code = 200
    return resp  #redirect(url_for('polls'))

####################################################################################
####################################################################################


@app.route("/polls")
def polls():
    polls = Poll.query.all()
    return polls_schema.jsonify(polls)


@app.route("/polls", methods=["POST"])
@login_required
def create_poll():
    poll, errors = poll_schema.load(request.form)
    if errors:
        resp = jsonify(errors)
        resp.status_code = 400
        return resp
    poll.user_id = current_user.id
    db.session.add(poll)
    db.session.commit()

    resp = jsonify({"message": "poll created"})
    resp.status_code = 201
    resp.headers["Location"] = poll.url
    return resp


@app.route("/polls/<int:id>")
def get_poll(id):
    poll = Poll.query.get_or_404(id)
    return poll_schema.jsonify(poll)


@app.route("/polls/<int:id>", methods=['PUT'])
@login_required
def change_poll(id):
    poll = Poll.query.get_or_404(id)
    if current_user.id == poll.user_id:
        if request.form['title']:
            poll.title = request.form['title']
            db.session.commit()
            resp = jsonify({'message': 'poll successfuly changed'})
            resp.status_code = 201
            return resp
        resp = jsonify({'error': 'Invalid title'})
        resp.status_code = 400
        return resp
    resp = jsonify({'error': 'access error'})
    resp.status_code = 400
    return resp

####################################################################################
####################################################################################


@app.route("/polls/<int:id>/questions")
def questions(id):
    poll = Poll.query.get_or_404(id)
    questions = Question.query.filter_by(poll_id=id)
    return questions_schema.jsonify(questions)


@app.route("/polls/<int:id>/questions", methods=['POST'])
@login_required
def create_question(id):
    poll = Poll.query.get_or_404(id)
    if current_user.id == poll.user_id:
        question, errors = question_schema.load(request.form)
        if errors:
            resp = jsonify(errors)
            resp.status_code = 400
            return resp
        question.poll_id = id
        db.session.add(question)
        db.session.commit()

        resp = jsonify({"message": "question successfuly created"})
        resp.status_code = 201
        resp.headers["Location"] = question.url
        return resp
    resp = jsonify({'error': 'access error'})
    resp.status_code = 400
    return resp


@app.route("/polls/<int:p_id>/questions/<int:id>")
def get_question(id, p_id):
    question = Question.query.get_or_404(id)
    return question_schema.jsonify(question)


@app.route("/polls/<int:p_id>/questions/<int:id>", methods=['PUT'])
@login_required
def change_question(p_id, id):
    poll = Poll.query.get_or_404(p_id)
    if current_user.id == poll.user_id:
        question = Question.query.get_or_404(id)
        if request.form['text']:
            question.text = request.form['text']
            db.session.commit()
            resp = jsonify({'message': 'question successfuly changed'})
            resp.status_code = 201
            return resp
        resp = jsonify({'error': 'Invalid input'})
        resp.status_code = 400
        return resp
    resp = jsonify({'error': 'access error'})
    resp.status_code = 400
    return resp

####################################################################################
####################################################################################


@app.route("/polls/<int:p_id>/questions/<int:id>/answers")
def answers(p_id, id):
    question = Question.query.get_or_404(id)
    answers = Answer.query.filter_by(question_id=id)
    return answers_schema.jsonify(answers)


@app.route("/polls/<int:p_id>/questions/<int:id>/answers", methods=['POST'])
@login_required
def create_answer(id, p_id):
    poll = Poll.query.get_or_404(p_id)
    if current_user.id == poll.user_id:
        answer, errors = answer_schema.load(request.form)
        if errors:
            resp = jsonify(errors)
            resp.status_code = 400
            return resp
        answer.question_id = id
        db.session.add(answer)
        db.session.commit()

        resp = jsonify({"message": "answer successfuly created"})
        resp.status_code = 201
        resp.headers["Location"] = answer.url
        return resp
    resp = jsonify({'error': 'access error'})
    resp.status_code = 400
    return resp


@app.route("/polls/<int:p_id>/questions/<int:q_id>/answers/<int:id>")
def get_answer(id, q_id, p_id):
    answer = Answer.query.get_or_404(id)
    return answer_schema.jsonify(answer)


@app.route("/polls/<int:p_id>/questions/<int:q_id>/answers/<int:id>", methods=['PUT'])
@login_required
def change_answer(p_id, q_id, id):
    poll = Poll.query.get_or_404(p_id)
    if current_user.id == poll.user_id:
        answer = Answer.query.get_or_404(id)
        if request.form['text']:
            answer.text = request.form['text']
            db.session.commit()
            resp = jsonify({'message': 'answer successfuly changed'})
            resp.status_code = 201
            return resp
        resp = jsonify({'error': 'Invalid input'})
        resp.status_code = 400
        return resp
    resp = jsonify({'error': 'access error'})
    resp.status_code = 400
    return resp


####################################################################################
####################################################################################


@app.errorhandler(404)
def page_not_found(error):
    resp = jsonify({"error":"not found"})
    resp.status_code = 404
    return resp


@app.errorhandler(401)
def unauthorized(error):
    resp = jsonify({"error":"unauthorized"})
    resp.status_code = 401
    return resp


@app.errorhandler(405)
def metod_not_allowed(error):
    resp = jsonify({"error":"method not allowed"})
    resp.status_code = 405
    return resp

if __name__ == '__main__':
    app.run()