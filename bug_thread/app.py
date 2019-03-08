from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException
from decouple import config
from .models import DB, User,Question,Answer
from dotenv import load_dotenv, find_dotenv
from flask import Flask, jsonify, redirect, render_template, session, url_for, request
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode
import datetime


def create_app():
  app = Flask(__name__)
  app.secret_key=config("SECRET_KEY")
  app.config['SQLALCHEMY_DATABASE_URI'] = config("DATABASE_URL")
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  DB.init_app(app)
  oauth = OAuth(app)

  auth0 = oauth.register(
    'auth0',
    client_id=config("CLIENT_ID"),
    client_secret=config("CLIENT_SECRET"),
    api_base_url=config("API_BASE_URL"),
    access_token_url=config("ACCESS_TOKEN_URL"),
    authorize_url= config("AUTHORIZE_URL"),
    client_kwargs={
      'scope': 'openid profile',
    },
  )

  def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
      if 'profile' not in session:
        # Redirect to Login page here
        return redirect('/')
      return f(*args, **kwargs)

    return decorated

  @app.route('/')
  def home():
    return render_template('home.html')

  @app.route('/callback')
  def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    db_user = (User.query.get(userinfo['sub']) or 
        User(id=userinfo['sub'], name = userinfo['name']))
    DB.session.add(db_user)
    DB.session.commit()
    return redirect('/dashboard')

  @app.route('/login')
  def login():
      return auth0.authorize_redirect(redirect_uri='http://127.0.0.1:5000/callback',
       audience='https://crawftv.auth0.com/userinfo')

  

  @app.route('/dashboard')
  @requires_auth
  def dashboard():
    return render_template('dashboard.html',
                          userinfo=session['profile'],
                          userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))
  

  @app.route('/logout')
  def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('home', _external=False), 'client_id': config('CLIENT_ID')}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

  @app.route('/users')
  @requires_auth
  def display_users_page():
    users = User.query.all()
    return render_template('users.html',users = users)

  @app.route('/q',methods=['POST','GET'])
  @requires_auth
  def display_questions():
    questions = Question.query.all()
    if request.method =='POST':
      text = request.values["text"]
      section = request.values['section']
      q = Question(text=text, user_id=session['profile']['user_id'], solved_status=False, date=datetime.datetime.now(),
        section = section)
      DB.session.add(q)
      DB.session.commit()
    return render_template('questions.html',questions=questions)
  
    
  return app