from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField,TimeField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, logout_user, login_user
import datetime





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SECRET_KEY'] = "msdcjfhskce"
db = SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

class Signup(FlaskForm):
    email = StringField("email", validators=[DataRequired("please enter your email")],render_kw={"class_":"form-input"})
    password = PasswordField("password",  validators=[DataRequired("password is required"), EqualTo("confirm", message="password does not match")],render_kw={"class_":"form-input"})
    confirm = PasswordField("password",  validators=[DataRequired("password is required"), EqualTo("confirm", message="password does not match")],render_kw={"class_":"form-input"})
    submit = SubmitField("sign up",render_kw={"id":"submit-button"})
    
class Add_task(FlaskForm):
    task = StringField("task", validators=[DataRequired()])
    time = TimeField("time")
    detail = TextAreaField("detail",validators=[Length(max=100)]) 
    submit = SubmitField("add")

class Login(FlaskForm):
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("password",  validators=[DataRequired("password is required")])
    submit = SubmitField("login",render_kw={"id":"submit-button"})
    

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    email =db.Column(db.String(25), unique=True,nullable=False)
    password = db.Column(db.String,nullable=True)
    task = db.relationship("Task", back_populates="user")

class Task(db.Model):
    __tablename__="task"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status_complete = db.Column(db.Boolean, nullable = False)
    task_name = db.Column(db.String(100),nullable=False)
    time= db.Column(db.Time(timezone=True),default=datetime.time, nullable=True)
    details = db.Column(db.String(200),nullable=True)
    user = db.relationship("User", back_populates="task")


with app.app_context():
    db.create_all()



@app.route('/')
def home():
    return render_template("index.html")



@app.route("/todo",methods=["POST","GET"])
def todo():
    add_task = Add_task()
    if add_task.validate_on_submit():
        print(type(add_task.time.data))
        with app.app_context():
            new_task = Task(status_complete=False,task_name=add_task.task.data,time=add_task.time.data,details=add_task.detail.data)
            db.session.add(new_task)
            db.session.commit()
    with app.app_context():
        task_list = db.session.query(Task).all()
        print(task_list)
    return render_template("todo.html", task_list=task_list, form=add_task)

@app.route("/login",methods=["POST","GET"])
def login():
    login_form = Login()
    if login_form.validate_on_submit():
        with app.app_context():
            user = db.session.query(User).filter_by(email=login_form.email.data).first()
            if user == None:
                flash("there's no account registered with this email")
            elif check_password_hash(user.password,login_form.password.data):
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("incorrect password")

    return render_template("login.html", form=login_form)



@app.route('/signup', methods=["POST","GET"])
def signup():
    signup_form =Signup()
    if signup_form.validate_on_submit():
        with app.app_context():
            new_user=User(email=signup_form.email.data, password=generate_password_hash(signup_form.password.data,salt_length=8))
            return redirect(url_for("login"))
    return render_template("signup.html", form=signup_form)


if __name__ == "__main__":
    app.run(debug=True)