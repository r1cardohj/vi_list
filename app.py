import os
import sys
import click

from flask import Flask,render_template,request,redirect,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_user,login_required, logout_user,current_user

#预处理 判断os
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
login_manager.login_view = 'login'

#创建Model
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20))  # 名字
    username = db.Column(db.String(20)) #账号名
    password_hash  = db.Column(db.String(128)) #密码哈希
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4)) #年份


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    # 全局的两个变量移动到这个函数内
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
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')

@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息

@app.cli.command()
@click.option('--username',prompt = True ,help = 'The username used to login')
@click.option('--pw',prompt = True ,help = 'The pw used to login')
def admin(username, pw):
    db.create_all
    
    user = User.query.first()
    if user is not None:
        click.echo('Upd user...')
        user.username = username
        user.set_password(pw)
    else:
        click.echo('Create user...')
        user = User(username=username, name='admin')
        user.set_password(pw)
        db.session.add(user)
    db.session.commit()
    click.echo('Done!')

@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    return user


@app.route('/')
def index():
    """index page

    Returns:
        _type_: template
    """
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html',user = user,movies = movies)


@app.errorhandler(404)
def page_not_found(e):
    user = User.query.first()
    return render_template('404.html',user=user),404


@app.route('/add',methods = ['GET','POST'])
@login_required
def add_movie_item():
    """add page
    
    """
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('非法输入')
            return redirect(url_for('index'))
        movie = Movie(title = title,year = year)
        db.session.add(movie)
        db.session.commit()
        flash('success!')
        return redirect(url_for('index'))
    
    return render_template('add_item.html')

@app.route('/movie/edit/<int:movie_id>',methods = ['GET','POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        
        if not title or not year or len(title) > 60 or len(year) > 4:
            flash('非法输入')
            return redirect(url_for('edit',movie_id = movie_id))
        
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('updated succeefully!')
        return redirect(url_for('index'))

    return render_template('edit.html',movie = movie)


@app.route('/movie/delete/<int:movie_id>', methods = ['POST'])
@login_required
def del_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('del successfully!')
    return redirect(url_for('index'))  # 重定向回主页

@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pw = request.form['pw']
        if not username or not pw:
            flash('are you kiding me?')
            return redirect(url_for(login))
        
        user = User.query.first()
        if username  == user.username and user.validate_password(pw):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))  # 重定向到主页
        flash('faild login')
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('logout bye')
    return redirect(url_for('index'))  # 重定向回首页

@app.route('/setting',methods=['POST','GET'])
@login_required
def setting():
    if request.method == 'POST':
        name = request.form['name']
        
        if not name or len(name) > 20:
            flash('非法输入')
            return redirect(url_for(setting))
        
        current_user.name = name
        db.session.commit()
        flash('setting successfully!')
    
    return render_template('setting.html')
        
        