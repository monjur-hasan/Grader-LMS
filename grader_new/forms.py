from flask_wtf import Form
from wtforms import (StringField, PasswordField, 
                    TextAreaField, RadioField,DateTimeField)
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                               Length, EqualTo, Required)
                               
from wtforms.fields.html5 import DateTimeLocalField

from models import User
from models import Course
from models import Assignment


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')

def course_exists(form, field):
    if Course.select().where(Course.name == field.data).exists():
        raise ValidationError('Course already exists.')

def course_assignment_exists(form, field):
    if Course.select().where(Course.name == field.data).exists():
        pass
    else:
        raise ValidationError('Course does not exist.')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')

def assginment_exists(form, field):
    if Assignment.select().where(Assignment.name == field.data).exists():
        raise ValidationError('Assignment already exists!')

def assginment_no_exists(form, field):
    
    if Assignment.select().where(Assignment.name == field.data).exists():
        print("x============x")
        pass
    else:    
        raise ValidationError('Assignment does not exist!')

    
def student_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        obj = User.get(User.email == field.data)
        if(obj.is_student==False):
            raise ValidationError('User is not student')
    else:
        raise ValidationError('User with that email does not exists.')

def parent_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        obj = User.get(User.email == field.data)
        if(obj.is_parent==False):
            raise ValidationError('User is not parent')
    else:
        raise ValidationError('User with that email does not exists.')

def student_course_enroll(form,field):
    obj = User.get(User.email == field.data)

    pass

def instructor_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        obj = User.get(User.email == field.data)
        if(obj.is_teacher==False):
            raise ValidationError('User is not Instructor')
    else:
        raise ValidationError('User with that email does not exists.')


class RegisterForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                         "numbers, and underscores only.")
            ),
            name_exists
        ])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
        ])

    category = RadioField('Category', 
            choices=[('teacher','Teacher'),('parent','Parent'),
                    ('student','Student')],
            validators=[DataRequired()])
    
class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class CreateCourse(Form):
    name = StringField('Name', validators=[DataRequired(),course_exists])
    description = TextAreaField('Description',validators=[DataRequired()])
    date = StringField('Schedule',validators=[DataRequired()])

class AddStudent(Form):
    c_name = StringField('Course Name', validators=[DataRequired(),
                                    course_assignment_exists])
    s_email = StringField('Student Email', validators=[DataRequired(),
                            student_exists])

class AddParent(Form):
    p_email = StringField('Parent Email', validators=[DataRequired(),
                          parent_exists])
    s_email = StringField('Student Email', validators=[DataRequired(),
                          student_exists])

class CreateAssignment(Form):
    a_name = StringField('Assignment Name', validators=[DataRequired(), 
                        assginment_exists])
    c_name = StringField('Course Name', validators=[DataRequired(),
                                    course_assignment_exists])

    due = DateTimeLocalField('Due Date',format="%Y-%m-%dT%H:%M", 
                                    validators=[DataRequired()])

class GradeStudent(Form):
    s_uname = StringField('Student Email', 
                            validators=[DataRequired(),student_exists])
    letter = StringField('Grade', validators=[DataRequired()])
    asg_name = StringField('Assignment ID', 
                            validators=[DataRequired(),assginment_no_exists])

class ReviewInstructor(Form):
    ins_email = StringField('Instructor Email',
                 validators=[DataRequired(),instructor_exists])
    description = TextAreaField('Your Review',validators=[DataRequired()])





