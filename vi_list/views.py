from vi_list import app,db
from .models import User,Movie
from flask import render_template,request,flash,redirect,url_for
from flask_login import login_required,login_user,logout_user,current_user

@app.route('/')
def index():
    """index page

    Returns:
        _type_: template
    """
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html',user = user,movies = movies)

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