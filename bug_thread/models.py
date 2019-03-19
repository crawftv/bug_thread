from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()

class User(DB.Model):
    id = DB.Column(DB.String, primary_key=True, unique =True)
    name = DB.Column(DB.String(30),nullable=False)
    email_verified = DB.Column(DB.Boolean,nullable=False)
    user_id = DB.Column(DB.String(30),nullable=False)
    


class Question(DB.Model):
    id = DB.Column(DB.Integer,primary_key=True)
    text = DB.Column(DB.Unicode(1500))
    user_id = DB.Column(DB.String,DB.ForeignKey('user.id'),
        nullable=False)
    solved_status = DB.Column(DB.Boolean,nullable=False)
    date = DB.Column(DB.DateTime)
    section = DB.Column(DB.String)
    answers = DB.relationship('Answer',backref='questions',
        lazy = True)
    user = DB.relationship('User',backref='questions',lazy=True)

class Answer(DB.Model):
    id =DB.Column(DB.Integer,primary_key=True)
    text = DB.Column(DB.Unicode(1500),nullable=False)
    user_id = DB.Column(DB.String,DB.ForeignKey('user.id'),
        nullable=False)
    is_solution = DB.Column(DB.Boolean,nullable=False)
    date = DB.Column(DB.DateTime)
    question_id = DB.Column(DB.Integer, DB.ForeignKey('question.id'),
        nullable=False)
    user = DB.relationship('User',backref='answers')
