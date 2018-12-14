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
    
        obj = models.Course.create(
            teacher=teacher,
            time=form.date.data,
            name=form.name.data,
            description=form.description.data
        )
        obj.student = student
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
                course = db_course,
                due=form.due.data
            )
            flash("Yay! Assignment created")
        
        else:
            flash("Sorry you're not instructor of this course!")
    return render_template("create_assignment.html",form=form)

@app.route('/addStudent', methods=('GET', 'POST'))
@login_required
def addStudent():
    form = forms.AddStudent()
    if form.validate_on_submit():
        user = form.s_email.data
        course = form.c_name.data

        db_course = models.Course.get(models.Course.name==course)
        db_user = models.User.get(models.User.email==user)

        db_course.student.add(db_user)
        flash("Student Added!")
    
    return render_template("add_student.html",form=form)

@app.route('/addParent', methods=('GET', 'POST'))
@login_required
def addParent():
    form = forms.AddParent()
    if form.validate_on_submit():
        p_email = form.p_email.data
        s_email = form.s_email.data
        parent_list = models.Parent.select()
        parent_exist = False
        parent_object = None
        chd_user = models.User.get(models.User.email==s_email)
        par_user = models.User.get(models.User.email==p_email)

        for p in parent_list:
            if p.parent.email == p_email:
                parent_exist = True
                parent_object = p

        if parent_exist:
            no_exists = True
            for child in parent_object.children:
                if child.email==s_email:
                    no_exists = False
                    flash("Parent was added before")

            if no_exists:  
                flash("Parent Added!")
                parent_object.children.add(chd_user)
                
        else:
            obj = models.Parent.create(parent=par_user)
            obj.children = chd_user
            flash("Parent Added")
        
    return render_template("add_parent.html",form=form)

@app.route('/grade', methods=('GET', 'POST'))
@login_required
def grade():
    form = forms.GradeStudent()
    if form.validate_on_submit():
        std = models.User.get(models.User.email==form.s_uname.data)

        asg = models.Assignment.get(models.Assignment.name==form.asg_name.data)
        models.Grade.create(
            student=std,
            letter = form.letter.data,
            assignement=asg
        )
        flash("Student successfully graded!")
    return render_template("grade_student.html",form=form)

@app.route('/stdSchedule')
@login_required
def stdSchedule():

    courses = {}
    obj = models.User.get(models.User.email==current_user.email)
    for course in obj.courses:
        courses[course.name]=[]
        courses[course.name].append(course.time)
        courses[course.name].append(course.teacher.username)
        courses[course.name].append(course.teacher.email)
    
    return render_template("student_schedule.html", courses=courses)

@app.route('/stdGrade')
@login_required
def stdGrade():

    obj = models.User.get(models.User.email==current_user.email)
    grades = models.Grade.select()
    grade_dict = {}
    for std in grades:
        if(std.student.email==current_user.email):
            assg = std.assignement.name 
            grade_dict[assg]=[]
            grade_dict[assg].append(std.assignement.course.name)
            grade_dict[assg].append(std.letter)
    
    return render_template("student_grades.html", courses=grade_dict)

@app.route('/stdAssignment')
@login_required
def stdAssignment():
    obj = models.User.get(models.User.email==current_user.email)
    list_courses = []
    asg_list = []

    asg = models.Assignment.select()
    for course in obj.courses:
            list_courses.append(course)

    for hw in asg:
        for course in list_courses:
            if hw.course.name == course.name:
                asg_list.append(hw)
    
    return render_template("student_assignments.html", assignments=asg)

@app.route('/parSchedule')
@login_required
def parSchedule():
    
    parnt = models.User.get(models.User.email==current_user.email)
    courses = []
    children = []

    """  for child in parnt.children:
        #print(parnt.children)
        children.append(child)
     """
    c_set = models.ChildrenParent.select()
    
    for child_id in c_set:
        child = models.User.get(models.User.id==child_id.user_id)
        if(child.username != "Admin"):
            children.append(child)

    main_count = 0
    for child in children:
        for course in child.courses:
            courses.append([])
            courses[main_count].append(child.username)
            courses[main_count].append(course.name)
            courses[main_count].append(course.time)
            courses[main_count].append(course.teacher.username)
            courses[main_count].append(course.teacher.email)
            main_count = main_count + 1
    
    return render_template("parent_schedule.html",courses=courses)

@app.route('/parGrade')
@login_required
def parGrade():

    parnt = models.User.get(models.User.email==current_user.email)
    courses = []
    children = []
    c_set = models.ChildrenParent.select()

    for child_id in c_set:
        child = models.User.get(models.User.id==child_id.user_id)
        if(child.username != "Admin"):
            children.append(child)
    
    grades = models.Grade.select()

    main_count = 0
    for child in children:
        for grade in grades:
            if(grade.student.email == child.email):
                courses.append([])
                courses[main_count].append(child.username)
                courses[main_count].append(grade.assignement.course.name)
                courses[main_count].append(grade.letter)
                main_count = main_count + 1
    
    return render_template("parent_grade.html", courses=courses)

@app.route('/reviewInstructor', methods=('GET', 'POST'))
@login_required
def reviewInstructor():
    form = forms.ReviewInstructor()
    if form.validate_on_submit():
        inst = models.User.get(models.User.email==form.ins_email.data)
        reviewer = models.User.get(models.User.email==current_user.email)
        models.Review.create(
            instructor = inst,
            discription = form.description.data,
            reviewer=reviewer
        )
        flash("Review sent to instructor!")
    
    return render_template("parent_review.html",form=form)

@app.route('/instReview')
@login_required
def instReview():
    reviews = models.Review.select()
    review_list = [] 

    for review in reviews:
        if review.instructor.email==current_user.email:
            critic = review.reviewer.username
            review_list.append([critic, review.discription])

    return render_template('inst_review.html', reviews = review_list)


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