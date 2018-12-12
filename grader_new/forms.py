from flask_wtf import Form
from wtforms import (StringField, PasswordField, 
                    TextAreaField, RadioField,DateTimeField)
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                               Length, EqualTo, Required)
                               
""" from wtforms.fields.html5 import DateTimeLocalField """

from models import User
from models import Course


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')

def course_exists(form, field):
    if Course.select().where(Course.name == field.data).exists():
        raise ValidationError('Course already exists.')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')

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
            choices=[('teacher','Teacher'),('parent','Parent'),('student','Student')],
            validators=[DataRequired()])
    
class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class CreateCourse(Form):
    name = StringField('Name', validators=[DataRequired(),course_exists])
    description = TextAreaField('Description',validators=[DataRequired()])
    """  time = DateTimeLocalField('Time of the Course', 
                            format='%Y-%m-%d %H:%M:%S', validators=[Required()]) """
    date = StringField('Days, Time', validators=[DataRequired()])

class AddStudent(Form):
    c_name = StringField('Course Name', validators=[DataRequired()])
    s_uname = StringField('Student Username', validators=[DataRequired()])

class AddParent(Form):
    c_name = StringField('Course Name', validators=[DataRequired()])
    s_uname = StringField('Parent Username', validators=[DataRequired()])

class CreateAssignment(Form):
    a_name = StringField('Assignment ID', validators=[DataRequired()])
    c_name = StringField('Course Name', validators=[DataRequired()])

class GradeStudent(Form):
    s_uname = StringField('Student Username', validators=[DataRequired()])
    letter = StringField('Grade', validators=[DataRequired()])
    asg_name = StringField('Assignment ID', validators=[DataRequired()])



