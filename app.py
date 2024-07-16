from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask import Flask, render_template, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash

from dotenv import load_dotenv
import os

from db import db
from decorators import admin_required, admin_or_self_required
from models import User, Role
from forms import LoginForm, RegisterForm, AddForm, UpdateForm

# load environment vars
load_dotenv()

# app initialisation
app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()


# home page
@app.route('/')
def index():
    current_username = current_user.username if current_user.is_authenticated else None
    current_id = current_user.id if current_user.is_authenticated else None
    return render_template('index.html', current_username=current_username, current_id=current_id)


# registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


# authentication page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', form=form)


# method for logging out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# page for list of users for admin
@app.route('/user')
@login_required
@admin_required
def info():
    users = (db.session.query(User.id, User.username, User.email, Role.role_name).join(Role)
             .order_by(User.id.asc()).all())
    return render_template('info.html', users=users)


# adding new user by admin page
@app.route('/user/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    form = AddForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data,
                        password=hashed_password, user_role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('info'))
    return render_template('add.html', form=form)


# updating user page
@app.route('/user/<int:user_id>/update', methods=['GET', 'POST'])
@login_required
@admin_or_self_required
def update(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdateForm(obj=user, user=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password = generate_password_hash(form.password.data).decode('utf-8')
        if current_user.role.role_name == 'admin' and 'role' in form:
            user.user_role = form.role.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', form=form, user=user)


# deleting user
@app.route('/user/<int:user_id>/delete', methods=['GET', 'POST'])
@login_required
@admin_or_self_required
def delete(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for('info'))


if __name__ == '__main__':
    app.run()
