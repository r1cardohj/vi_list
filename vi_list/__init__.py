import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

#实例化app和dp配置 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)

@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    return user



from vi_list import views, errors, commands
from vi_list.models import User, Movie
