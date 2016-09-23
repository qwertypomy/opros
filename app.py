import os
from flask import Flask, jsonify, request, url_for, redirect, session
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


@app.route("/")
def index():
    return redirect(url_for('polls'))


@app.route("/polls/")
def polls():
    all_polls = Poll.query.all()
    return polls_schema.jsonify(all_polls)


@app.route("/polls/", methods=["POST"])
#@login_required
def create_poll():
		req = requset.form
		#req['user'] = url_for(current_user)
		poll, errors = poll_schema.load(req)
		if errors:
				resp = jsonify(errors)
				resp.status_code = 400
				return resp
		db.session.add(poll)
		db.session.commit()

		resp = jsonify({"message": "poll created"})
		resp.status_code = 201
		resp.headers["Location"] = poll.url
		return resp


@app.route("/profile/")
@login_required
def user_profile():
	return user_schema.jsonify(current_user)    


@app.route("/registration/", methods=['POST'])
def registration():
		try: 
			user = User(request.form)
			db.session.add(user)
			db.session.commit()

			resp = jsonify({"message": "registration successful"})
			resp.status_code = 201
			resp.headers["Location"] = user.url
			return resp
		except: 
			return jsonify({'message':'error'})


@app.route("/registration/")
def assdsada():
			user = User(login='login123da', password='password123', user_name='misha')
			db.session.add(user)
			db.session.commit()
			resp = jsonify({"message": "registration successful"})
			return resp
		

@app.route("/polls/<int:id>")
def get_poll(id):
		poll = Poll.query.get_or_404(id)
		return poll_schema.jsonify(poll)


@app.route("/users/<int:id>")
def get_user(id):
		user = User.query.get_or_404(id)
		return user_schema.jsonify(poll)


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


if __name__ == '__main__':
    app.run()