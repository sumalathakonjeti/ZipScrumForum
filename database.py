from app import app
from flask_login import UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
import re
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

db = SQLAlchemy(app)
password_regex = re.compile("^[a-zA-Z0-9!@#%&]{6,40}$")
username_regex = re.compile("^[a-zA-Z0-9!@#%&]{4,40}$")


# Account checks
def username_taken(username):
    return User.query.filter(User.username == username).first()


def email_taken(email):
    return User.query.filter(User.email == email).first()


def valid_username(username):
    if not username_regex.match(username):
        # username does not meet password reqirements
        return False
    # username is not taken and does meet the password requirements
    return True


def valid_password(password):
    return password_regex.match(password)


# Post checks
def valid_title(title):
    return len(title) > 4 and len(title) < 140


def valid_content(content):
    return len(content) > 10 and len(content) < 5000


def link_taken(link):
    return Languages.query.filter(Languages.links == link).first()


# OBJECT MODELS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.VARCHAR(20), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    email = db.Column(db.VARCHAR(500), unique=True, nullable=False)
    admin = db.Column(db.Boolean, default=False)
    login_attempts = db.Column(db.Integer, default=0)
    posts = db.relationship("Post", backref="user")
    comments = db.relationship("Comment", backref="user")
    tags = db.relationship("Tags", backref="user")
    message = db.relationship("Message", backref="user")
    languages = db.relationship("Languages", backref="user")


    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    comments = db.relationship("Comment", backref="post")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subforum_id = db.Column(db.Integer, db.ForeignKey('subforum.id'))
    postdate = db.Column(db.DateTime)
    tags = db.relationship("Tags", backref="post")

    # cache stuff
    lastcheck = None
    savedresponce = None

    def __init__(self, title, content, postdate):
        self.title = title
        self.content = content
        self.postdate = postdate

    def get_time_string(self):
        # this only needs to be calculated every so often, not for every request
        # this can be a rudamentary chache
        now = datetime.datetime.now()
        if self.lastcheck is None or (now - self.lastcheck).total_seconds() > 30:
            self.lastcheck = now
        else:
            return self.savedresponce

        diff = now - self.postdate

        seconds = diff.total_seconds()
        print(seconds)
        if seconds / (60 * 60 * 24 * 30) > 1:
            self.savedresponce = " " + str(int(seconds / (60 * 60 * 24 * 30))) + " months ago"
        elif seconds / (60 * 60 * 24) > 1:
            self.savedresponce = " " + str(int(seconds / (60 * 60 * 24))) + " days ago"
        elif seconds / (60 * 60) > 1:
            self.savedresponce = " " + str(int(seconds / (60 * 60))) + " hours ago"
        elif seconds / (60) > 1:
            self.savedresponce = " " + str(int(seconds / 60)) + " minutes ago"
        else:
            self.savedresponce = "Just a moment ago!"

        return self.savedresponce


class Subforum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.VARCHAR(500), unique=True)
    description = db.Column(db.Text)
    subforums = db.relationship("Subforum")
    parent_id = db.Column(db.Integer, db.ForeignKey('subforum.id'))
    posts = db.relationship("Post", backref="subforum")
    path = None
    hidden = db.Column(db.Boolean, default=False)

    def __init__(self, title, description):
        self.title = title
        self.description = description


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    postdate = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))

    lastcheck = None
    savedresponce = None

    def __init__(self, content, postdate):
        self.content = content
        self.postdate = postdate

    def get_time_string(self):
        # this only needs to be calculated every so often, not for every request
        # this can be a rudamentary chache
        now = datetime.datetime.now()
        if self.lastcheck is None or (now - self.lastcheck).total_seconds() > 30:
            self.lastcheck = now
        else:
            return self.savedresponce

        diff = now - self.postdate
        seconds = diff.total_seconds()
        if seconds / (60 * 60 * 24 * 30) > 1:
            self.savedresponce = " " + str(int(seconds / (60 * 60 * 24 * 30))) + " months ago"
        elif seconds / (60 * 60 * 24) > 1:
            self.savedresponce = " " + str(int(seconds / (60 * 60 * 24))) + " days ago"
        elif seconds / (60 * 60) > 1:
            self.savedresponce = " " + str(int(seconds / (60 * 60))) + " hours ago"
        elif seconds / (60) > 1:
            self.savedresponce = " " + str(int(seconds / 60)) + " minutes ago"
        else:
            self.savedresponce = "Just a moment ago!"
        return self.savedresponce


class Tags(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.Text)
    post_info = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __init__(self, type, post_info):
        self.type = type
        self.post_info = post_info


class Languages(db.Model):
    lan_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.Text)
    links = db.Column(db.Text)

    def __init__(self, type, links):
        # self.user_id = user_id
        self.type = type
        self.links = links


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.VARCHAR(500))
    username = db.Column(db.VARCHAR(500))
    message = db.Column(db.VARCHAR(500))
    postdate = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # sender = db.Column(db.VARCHAR(500), db.ForeignKey('user.username'))

    lastcheck = None
    savedresponce = None

    def __init__(self, sender, message, postdate):
        self.sender = sender
        self.message = message
        self.postdate = postdate
        self.username = current_user.username

    def get_time_string(self):
        # this only needs to be calculated every so often, not for every request
        # this can be a rudamentary chache
        now = datetime.datetime.now()
        if self.lastcheck is None or (now - self.lastcheck).total_seconds() > 30:
            self.lastcheck = now
        else:
            return self.savedresponce

        diff = now - self.postdate
        seconds = diff.total_seconds()
        if seconds / (60 * 60 * 24 * 30) > 1:
            self.savedresponce = " " + str(int(seconds / (60 * 60 * 24 * 30))) + " months ago"
        elif seconds / (60 * 60 * 24) > 1:
            self.savedresponce = " " + str(int(seconds / (60 * 60 * 24))) + " days ago"
        elif seconds / (60 * 60) > 1:
            self.savedresponce = " " + str(int(seconds / (60 * 60))) + " hours ago"
        elif seconds / (60) > 1:
            self.savedresponce = " " + str(int(seconds / 60)) + " minutes ago"
        else:
            self.savedresponce = "Just a moment ago!"
        return self.savedresponce


class UpdateAccount(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Update')
