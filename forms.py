# forms.py
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional

from models import User, Role


# registration form
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=320)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=256)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        username_taken = User.query.filter_by(username=username.data).first()
        if username_taken:
            raise ValidationError('Username already exists')

    def validate_email(self, email):
        email_taken = User.query.filter_by(email=email.data).first()
        if email_taken:
            raise ValidationError('Email already exists')


# authentication form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=256)])
    submit = SubmitField('Login')


# adding new user form
class AddForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=320)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=256)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add')

    def __init__(self, *args, **kwargs):
        super(AddForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.role_name) for role in Role.query.order_by(Role.role_name).all()]

    def validate_username(self, username):
        username_taken = User.query.filter_by(username=username.data).first()
        if username_taken:
            raise ValidationError('Username already exists')

    def validate_email(self, email):
        email_taken = User.query.filter_by(email=email.data).first()
        if email_taken:
            raise ValidationError('Email already exists')


# updating user fields form
class UpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=320)])
    password = PasswordField('Password', validators=[Optional(), Length(min=8, max=256)])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Update')

    def __init__(self, user, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.user = user

        if current_user.role.role_name == 'admin':
            roles = [(role.id, role.role_name) for role in Role.query.all()]
            default_role_id = self.user.user_role
            self.role.choices = [(role[0], role[1]) for role in roles if role[0] == default_role_id] + \
                                [(role[0], role[1]) for role in roles if role[0] != default_role_id]
        else:
            del self.role

    def validate_username(self, username):
        if username.data != self.user.username:
            username_taken = User.query.filter_by(username=username.data).first()
            if username_taken:
                raise ValidationError('Username already exists')

    def validate_email(self, email):
        if email.data != self.user.email:
            email_taken = User.query.filter_by(email=email.data).first()
            if email_taken:
                raise ValidationError('Email already exists')
