import csv
from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo

app = Flask(__name__)
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

class RegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Password', validators=[DataRequired(), EqualTo('password')])
    address = StringField('Address', validators = [DataRequired()])
    address2 = StringField('Address 2')
    city = StringField('City', validators = [DataRequired()])
    submit = SubmitField('Sign Up')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_patient = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.is_patient}')"

class LocatorForm(FlaskForm):
    practice_name = StringField('Search by Practice Name')
    speciality = SelectField('Speciality', choices = ['Choose a Category', 'Anesthesiology', 'Chiropractor', 'Orthodentist', 'Dermatology', 'Neurology', 'Pathology', 'Psychiatry', 'Surgery', 'Urology', 'Dermatology', 'Chiropractor', 'Dental', 'Anesthesiology', 'Cardiology', 'Gastroenterology', 'Psychiatry', 'Surgery', 'Radiology', 'Psychiatry', 'Urology', 'Gastroenterology', 'Hepatology', 'Dental', 'Orthodentist', 'Surgery', 'Neurology', 'Cardiology', 'Immunology', 'Psychiatry'])
    radius = SelectField('Radius', choices = [str(i) + ' miles' for i in [5, 10, 20, 50, 75]])
    city_zip = StringField('City or Zip')
    submit = SubmitField('Search')

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
    form = LocatorForm()
    return render_template('index.html', underline = 'home', form = form)

@app.route("/about")
def about():
    return render_template('aboutus.html', underline = 'about')

@app.route("/locator")
def locator():
    print(request.args)
    print('In locator')
    form = LocatorForm(request.args, csrf_enabled=False)
    results = None
    if form.validate():
        print('In validate submit')

        if not form.practice_name.data:
            form.practice_name.data = ''
        if not form.city_zip.data:
            form.city_zip.data = ''
        if form.speciality.data == 'Choose a Category':
            form.speciality.data = ''
        is_zip = form.city_zip.data.isdigit()
        if is_zip:
            results = Affiliate.query.filter(Affiliate.name.ilike(f'%{ form.practice_name.data.strip() }%')).filter(Affiliate.speciality.ilike(f'%{ form.speciality.data.strip() }%')).filter(Affiliate.zip_code == form.city_zip.data.strip())
        else:
            results = Affiliate.query.filter(Affiliate.name.ilike(f'%{ form.practice_name.data.strip() }%')).filter(Affiliate.speciality.ilike(f'%{ form.speciality.data.strip() }%')).filter(Affiliate.city.ilike(f'%{ form.city_zip.data.strip() }%'))
        sort_name = request.args.get('sort_name')
        if sort_name == 'A':
            results = results.order_by(Affiliate.name)
        elif sort_name == 'D':
            results = results.order_by(Affiliate.name.desc())
        results = results.paginate(per_page = 100)
    return render_template('locator.html', underline = 'locator', form = form, results = results)

@app.route("/doctors/", defaults={'page_num': 1})
@app.route("/doctors/<int:page_num>/")
def doctors(page_num):
    doctors = Affiliate.query.paginate(per_page = 10, page = page_num)
    print(page_num)
    return render_template('doctors.html', underline = 'doctors', doctors = doctors)

@app.route("/contact")
def contact():
    return render_template('contact.html', underline = 'contact')

@app.route("/register")
def signup():
    return render_template('signup.html')

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
            flash(f'{ user.username } has logged in', 'success')
            return redirect(url_for('home'))
            #return f"<h1> { user.username } has logged in"
        else:
            flash(f'Login failed', 'danger')
            return redirect(url_for('home'))
    else:
        return render_template('login.html', form = form)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
