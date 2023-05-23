import os
import sys
import click

from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy

#预处理 判断os
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

#实例化app和dp配置 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data_db') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#创建Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20))  # 名字


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4)) #年份


@app.cli.command()
def forge():
    """insert init db record
    """
    db.create_all()
    
    name = 'hj'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add()
    db.session.commit()
    click.echo('Done')


@app.route('/')
def index():
    """index page

    Returns:
        _type_: template
    """
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html',user = user,movies = movies)