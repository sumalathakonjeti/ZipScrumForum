from flask import Flask
from flask_mail import Mail
import os

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
username = os.getenv('MYSQL_user')
pswd = os.getenv('MYSQL_pw')
email_usr = os.getenv('email_usr')
email_pwd = os.getenv('email_pw')
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://' + username + ":" + pswd + '@localhost/posts'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE-TLS'] = True
app.config['MAIL_USERNAME'] = email_usr
app.config['MAIL_PASSWORD'] = email_pwd
mail = Mail(app)