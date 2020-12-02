import os
from app import app

SECRET_KEY = os.environ['SECRET_KEY']
#SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SITE_NAME = "Default Forum Name"
SITE_DESCRIPTION = "Change this value in config.py"
username = os.getenv('MYSQL_user')
pswd = os.getenv('MYSQL_pw')
#SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/database.db";
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://' + username + ":" + pswd + '@localhost/posts'


