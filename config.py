import os
from flask_mail import Mail
from app import app

SECRET_KEY = os.environ['SECRET_KEY']
SITE_NAME = "Zip Code Cafe"
SITE_DESCRIPTION = "Where knowledge is power"
username = os.getenv('MYSQL_user')
pswd = os.getenv('MYSQL_pw')
email_usr = os.getenv('email_usr')
email_pwd = os.getenv('email_pw')
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://' + username + ":" + pswd + '@localhost/posts'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = email_usr
app.config['MAIL_PASSWORD'] = email_pwd
mail = Mail(app)

