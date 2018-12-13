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
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            teacher=teacher_b,
            parent=parent_b,
            student=student_b
        )
        return redirect(url_for('login'))
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

@app.route('/')
def homepage():
    return render_template("index.html")


@app.route('/profile')
@login_required
def index():
    print(current_user)
    if(current_user.is_teacher):
        courses = models.Course.select()
        course_list = []
        for course in courses:
            if(course.teacher.email==current_user.email):
                course_list.append(course)

        return render_template("instructor.html",courses=course_list)
    elif(current_user.is_parent):
        return render_template("parent.html")
    else:
        return render_template("student.html")
    return "Not found"

@app.route('/createCourse', methods=('GET', 'POST'))
@login_required
def createCourse():
    form = forms.CreateCourse()
    if form.validate_on_submit():
        teacher = models.User.get(models.User.email==current_user.email)
        student = models.User.get(models.User.email=="admin@admin.com")
    
        models.Course.create_course(
            teacher,
            form.date.data,
            form.name.data,
            form.description.data
        )
        flash("Course successfully created!")
        return redirect(url_for('createCourse'))

    return render_template("create_course.html",form=form)

@app.route('/createAssignment', methods=('GET', 'POST'))
@login_required
def createAssignment():
    form = forms.CreateAssignment()
    if form.validate_on_submit():
        course = form.c_name.data
        name = form.a_name.data

        db_course = models.Course.get(models.Course.name==course)
        if(db_course.teacher.username==current_user.username):
            models.Assignment.create_assignment(
                name = form.a_name.data,
                course = db_course
            )
            flash("Yay!! Course created")
        
        else:
            flash("Sorry you're not instructor of this course!")
    return render_template("create_assignment.html",form=form)

@app.route('/addStudent', methods=('GET', 'POST'))
@login_required
def addStudent():
    form = forms.AddStudent()
    if form.validate_on_submit():
        email = form.s_email.data
        course = form.c_name.data

        db_course = models.Course.get(models.Course.name==course)
        db_email = models.User.get(models.User.email==email)
        



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('login'))
        

if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='Admin',
            email='admin@admin.com',
            password='admin',
            teacher=False, parent=False, student=True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)