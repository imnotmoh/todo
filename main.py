from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField,TimeField, TextAreaField, RadioField, widgets, SelectMultipleField
from wtforms.validators import DataRequired, EqualTo, Length, Optional
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, logout_user, login_user, login_required, UserMixin
from datetime import datetime






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
    task = StringField("task", validators=[DataRequired(message="required")])
    time = TimeField("time", validators=[Optional()])
    detail = TextAreaField("detail",validators=[Length(max=100)]) 
    submit = SubmitField("add", render_kw={"form":"form2"})



class Login(FlaskForm):
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("password",  validators=[DataRequired("password is required")])
    submit = SubmitField("login",render_kw={"id":"submit-button"})

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class Complete (FlaskForm):
    complete = MultiCheckboxField("",choices=" ",render_kw={"id":"check"})

class User(db.Model, UserMixin):
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
    task_date = db.Column(db.Date, nullable=False)
    time= db.Column(db.Time(timezone=True),default=datetime.time, nullable=True)
    details = db.Column(db.String(200),nullable=True)
    user = db.relationship("User", back_populates="task", order_by='Task.time')


with app.app_context():
     db.create_all()



@app.route('/')
def home():
    return redirect(url_for('login'))



@app.route("/todo",methods=["POST","GET"])
@login_required
def todo():
    complete_radio = Complete()
    
    add_task = Add_task()
    print(add_task.validate_on_submit())
    if add_task.validate_on_submit():
        print(type(add_task.time.data))
        with app.app_context():
            new_task = Task(status_complete=False,task_name=add_task.task.data,time=add_task.time.data,details=add_task.detail.data, user=current_user,task_date=datetime.now().date())
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('todo'))
    with app.app_context():
        task_list = db.session.query(Task).filter_by(user_id=current_user.id).order_by(Task.time).all() # type: ignore 
        now =datetime.now().date()
        
        for task in task_list:
            how_long = now - task.task_date
            if task.status_complete and how_long.days > 2:
                with app.app_context():
                    task_delete = db.session.query(Task).get(task.id)
                    db.session.delete(task_delete)
                    db.session.commit()
                task_list.remove(task)
        
        
    
    return render_template("todo.html", task_list=task_list, form=add_task, complete=complete_radio,user=current_user)

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
                return redirect(url_for("todo"))
            else:
                flash("incorrect password")

    return render_template("login.html", form=login_form,user=current_user)



@app.route('/signup', methods=["POST","GET"])
def signup():
    signup_form =Signup()
    if signup_form.validate_on_submit():
        with app.app_context():
            new_user=User(email=signup_form.email.data, password=generate_password_hash(signup_form.password.data,salt_length=8))
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
    return render_template("signup.html", form=signup_form, user=current_user)

@app.route('/submit_checkbox', methods=['POST'])
def submit_checkbox():
    id = request.json["id"] # type: ignore 
    isChecked = request.json['isChecked'] # type: ignore 
    with app.app_context():
        completed_check = db.session.query(Task).get(id)
        completed_check.status_complete = True
        db.session.commit()
    return jsonify({'status': 'success'})

@app.route("/signout")
def signout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/delete")
def delete():
    id = request.args.get('id')
    with app.app_context():
        task = db.session.query(Task).get(id)
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('todo'))


   
    

if __name__ == "__main__":
    app.run(debug=True)
