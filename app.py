from flask import Flask,render_template

app = Flask(__name__)

NAME = 'hj'
MOVIES = [{'title':'银河护卫队','year':2023,'view_date':"1999-1-23"},
          {'title':'复仇者联盟','year':2011,'view_date':"1999-12-31"}]

@app.route('/')
def index():
    return render_template('index.html',name = NAME,movies = MOVIES)