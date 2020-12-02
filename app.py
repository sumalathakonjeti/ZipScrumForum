from flask import Flask
import os
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
username = os.getenv('MYSQL_user')
pswd = os.getenv('MYSQL_pw')
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://' + username + ":" + pswd + '@localhost/posts'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI