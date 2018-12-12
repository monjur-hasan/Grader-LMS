from flask import (Flask, g, render_template, flash, redirect, url_for,
                  abort, )
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (LoginManager, login_user, logout_user,
                             login_required, current_user)

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'auoejsh.bouoastuh.43,uoausoehuosth3ououea.auoub!'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Yay, you registered!", "success")
        teacher_b = True if form.category.data == "teacher" else False
        parent_b = True if form.category.data == "parent" else False
        student_b = True if form.category.data == "student" else False
        print(current_user)
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            teacher=teacher_b,
            parent=parent_b,
            student=student_b
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)

@app.route('/', methods=('GET', 'POST'))
def index():
    form = forms.CreateCourse()
    
    if form.validate_on_submit():
        form = forms.CreateCourse()
        print(form.date.data)
        return redirect(url_for('login'))
        
    return render_template("create_course.html")


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='grader',
            email='grader@grader.com',
            password='grader',
            teacher=True, parent=False, student=False
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)