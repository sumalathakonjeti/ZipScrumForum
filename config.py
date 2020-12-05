import os
from app import app

SECRET_KEY = os.environ['SECRET_KEY']
#SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SITE_NAME = "Zip Code Cafe"
SITE_DESCRIPTION = "Where knowledge is power"
username = os.getenv('MYSQL_user')
pswd = os.getenv('MYSQL_pw')
#SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/database.db";
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://' + username + ":" + pswd + '@localhost/posts'
