import os
from flask import Flask, jsonify, request, url_for, redirect, session
from flask_login import LoginManager, current_user, login_required, \
    login_user, logout_user
from flask_oauthlib.client import OAuth
from datetime import datetime
from models import db, User, Poll, Question, Answer
from schemas import ma, user_schema, users_schema, poll_schema, \
    polls_schema, answer_schema, answers_schema, \
    question_schema, questions_schema
from werkzeug.security import check_password_hash
from crossdomain import crossdomain

login_manager = LoginManager()


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
ma.init_app(app)
login_manager.init_app(app)
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()

@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.args.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user
    return None


@app.route("/")
@crossdomain(origin='*')
def index():
    return redirect(url_for('polls'))


@app.route("/users")
@crossdomain(origin='*')
def users():
    all_users = User.query.all()
    return users_schema.jsonify(all_users)


@app.route("/users/<int:id>")
@crossdomain(origin='*')
def get_user(id):
    if current_user.is_authenticated and current_user.id == id:
        return redirect(url_for('profile'))
    user = User.query.get_or_404(id)
    return user_schema.jsonify(user)


@app.route("/profile")
@crossdomain(origin='*')
def profile():
    if 'google_token' in session:
        me = google.get('userinfo')
        user = User.query.filter_by(email=me.data['email']).first_or_404()
        return user_schema.jsonify(user)
    return redirect(url_for('login'))


@app.route("/profile", methods=['PUT'])
@crossdomain(origin='*')
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


############################################################

@app.route('/login')
@crossdomain(origin='*')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
@crossdomain(origin='*')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
@crossdomain(origin='*')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')

    user = User.query.filter_by(email=me.data['email']).one_or_none()
    if(not user):
        user = User(me.data['email'], me.data['name'])
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(email=me.data['email']).first_or_404()
    login_user(user)

    resp = jsonify({"message": "login successful"})
    resp.status_code = 201
    resp.headers["Location"] = user.url
    return resp


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

############################################################




####################################################################################
####################################################################################


@app.route("/polls")
@crossdomain(origin='*')
def polls():
    polls = Poll.query.all() #Poll.query.all().order_by(viewers_number).limit(30)
    return polls_schema.jsonify(polls)


@app.route("/polls", methods=["POST"])
@crossdomain(origin='*')
@login_required
def create_poll():
    poll, errors = poll_schema.load(request.form)
    if errors:
        resp = jsonify(errors)
        resp.status_code = 400
        return resp
    poll.user_id = current_user.id
    poll.timestamp = datetime.utcnow()
    db.session.add(poll)
    db.session.commit()

    resp = jsonify({"message": "poll created"})
    resp.status_code = 201
    resp.headers["Location"] = poll.url
    return resp


@app.route("/polls/<int:id>")
@crossdomain(origin='*')
@login_required
def get_poll(id):
    poll = Poll.query.get_or_404(id)
    u = poll.add_viewer(current_user)
    db.session.add(u)
    db.session.commit()
    return poll_schema.jsonify(poll)


@app.route("/polls/<int:id>", methods=['PUT'])
@crossdomain(origin='*')
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
@crossdomain(origin='*')
def questions(id):
    poll = Poll.query.get_or_404(id)
    questions = Question.query.filter_by(poll_id=id)
    return questions_schema.jsonify(questions)


@app.route("/polls/<int:id>/questions", methods=['POST'])
@crossdomain(origin='*')
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
        if question.def_answer is None:
            question.def_answer=False
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
@crossdomain(origin='*')
def get_question(id, p_id):
    question = Question.query.get_or_404(id)
    return question_schema.jsonify(question)


@app.route("/polls/<int:p_id>/questions/<int:id>", methods=['PUT'])
@crossdomain(origin='*')
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
@crossdomain(origin='*')
def answers(p_id, id):
    Question.query.get_or_404(id)
    answers = Answer.query.filter_by(question_id=id)
    return answers_schema.jsonify(answers)


@app.route("/polls/<int:p_id>/questions/<int:id>/answers", methods=['POST'])
@crossdomain(origin='*')
@login_required
def create_answer(id, p_id):
    poll = Poll.query.get_or_404(p_id)
    Question.query.get_or_404(id)
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
@crossdomain(origin='*')
def get_answer(id, q_id, p_id):
    answer = Answer.query.get_or_404(id)
    return answer_schema.jsonify(answer)


@app.route("/polls/<int:p_id>/questions/<int:q_id>/answers/<int:id>", methods=['PUT'])
@crossdomain(origin='*')
@login_required
def change_answer(p_id, q_id, id):
    poll = Poll.query.get_or_404(p_id)
    Question.query.get_or_404(q_id)
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


@app.route("/polls/<int:p_id>/questions/<int:q_id>/answers/<int:id>", methods=['POST'])
@crossdomain(origin='*')
@login_required
def reply(id, q_id, p_id):
    Poll.query.get_or_404(p_id)
    question = Question.query.get_or_404(q_id)
    if question.def_answer:
        answers = question.answers
        for answer in answers:
            a_id = answer.id
            a = Answer.query.get_or_404(a_id)
            users = a.user
            for user in users:
                if user.id == current_user.id:
                    answer.cancel_reply(current_user)
                    break
    answer = Answer.query.get_or_404(id)
    u = answer.reply(current_user)
    db.session.add(u)
    db.session.commit()
    resp = jsonify({'message': 'reply successfuly adopted'})
    resp.status_code = 201
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

@app.errorhandler(500)
def internal_server_error(error):
    resp = jsonify({"error":"internal server error"})
    resp.status_code = 500
    return resp


if __name__ == '__main__':
    app.run()