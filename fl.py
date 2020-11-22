import csv
from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'f0799c2163525275f109b3c7893ac4fe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

with open('data.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    data = list(csv_reader)
    headers = data[0]
    data = data[1:]

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_patient = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.is_patient}')"

class Affiliate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    speciality = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    state = db.Column(db.String(25), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Affiliate('{self.name}', '{self.speciality}', '{self.city}')"

def match_rows(speciality = None, city = None, state = None, zip_code = None):
    results = []
    for row in data:
        # ['2', 'B', 'Vision', 'Trenton', 'HD', '97654', 'white 645']
        if (speciality == row[2] or not speciality) and (city == row[3] or not city) and (state == row[4] or not state) and (zip_code == row[5] or not zip_code):
            results.append(row)
    return results

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/all")
def all():
    return render_template('table.html', headers = headers, results = data, title = 'All Providers')

@app.route("/state/", defaults={'state': None})
@app.route("/state/<state>")
def get_state_data(state):
    results = match_rows(state = state)
    return render_template('table.html', headers = headers, results = results, title = f'{ state } Providers')

@app.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and user.password == form.password.data:
            return f"<h1> { user.username } has logged in"
        else:
            return redirect("https://example.com/fail")
    else:
        return render_template('login.html', form = form)

if __name__ == '__main__':
    app.run(debug=True)
