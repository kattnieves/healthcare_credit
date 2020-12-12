import os
import re
import csv
from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import googlemaps
from pprint import pprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AIzaSyCOzJQ27CWQx8en2SzFhVDOfuqNLzN3eeY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['GOOGLEMAPS_KEY'] = "AIzaSyCOzJQ27CWQx8en2SzFhVDOfuqNLzN3eeY"
app.config['UPLOADS'] = 'uploads'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
maps = googlemaps.Client(key = app.config['GOOGLEMAPS_KEY'])
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators = [DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min = 8, max = 256)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message = 'Both the passwords should match.')])
    address = StringField('Address', validators = [DataRequired()])
    address2 = StringField('Address 2')
    city = StringField('City', validators = [DataRequired()])
    state = SelectField('State', choices = ['AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'GU', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'MP', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VI', 'VA', 'WA', 'WV', 'WI', 'WY'])
    zip_code = IntegerField('Zip Code', validators = [DataRequired(message = 'Enter a valid Zip Code.')])
    is_doctor = RadioField('Are you a Doctor?', choices=[('Yes','You are a doctor. You will have CSV upload access but no apply access.'),('No','You are a patient. You will need this option to apply to an Affiliate.')], default = 'No', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

    def validate_password(self, password):
        if not re.fullmatch(r'(?=[^\d\n]*\d)(?=[^A-Z\n]*[A-Z])(?=[^a-z\n]*[a-z])^[A-Za-z0-9]{8,}$', password.data):
            raise ValidationError('Your password is weak. Password must have 8 or more characters with a mix of uppercase letters, lowercase letters and numbers.')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable = False)
    address = db.Column(db.String(100), nullable = False)
    address2 = db.Column(db.String(100), nullable = True)
    city = db.Column(db.String(20), nullable = False)
    state = db.Column(db.String(20), nullable = False)
    zip_code = db.Column(db.Integer, nullable = False)
    is_doctor = db.Column(db.Boolean, nullable = False)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.is_doctor}')"

class LocatorForm(FlaskForm):
    practice_name = StringField('Search by Practice Name')
    speciality = SelectField('Speciality', choices = ['Choose a Category', 'Anesthesiology', 'Chiropractor', 'Orthodentist', 'Dermatology', 'Neurology', 'Pathology', 'Psychiatry', 'Surgery', 'Urology', 'Dermatology', 'Chiropractor', 'Dental', 'Anesthesiology', 'Cardiology', 'Gastroenterology', 'Psychiatry', 'Surgery', 'Radiology', 'Psychiatry', 'Urology', 'Gastroenterology', 'Hepatology', 'Dental', 'Orthodentist', 'Surgery', 'Neurology', 'Cardiology', 'Immunology', 'Psychiatry'])
    radius = SelectField('Radius', choices = [str(i) + ' miles' for i in [5, 10, 20, 50, 75]])
    city_zip = StringField('City or Zip', validators = [DataRequired()])
    submit = SubmitField('Search')

class ProviderForm(FlaskForm):
    practice_name = StringField('Search by Practice Name')
    speciality = SelectField('Speciality', choices = ['Choose a Category', 'Anesthesiology', 'Chiropractor', 'Orthodentist', 'Dermatology', 'Neurology', 'Pathology', 'Psychiatry', 'Surgery', 'Urology', 'Dermatology', 'Chiropractor', 'Dental', 'Anesthesiology', 'Cardiology', 'Gastroenterology', 'Psychiatry', 'Surgery', 'Radiology', 'Psychiatry', 'Urology', 'Gastroenterology', 'Hepatology', 'Dental', 'Orthodentist', 'Surgery', 'Neurology', 'Cardiology', 'Immunology', 'Psychiatry'])
    submit = SubmitField('Search')

class Affiliate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    speciality = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    state = db.Column(db.String(25), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Integer, nullable=False)
    longitude = db.Column(db.Integer, nullable=False)
    is_provider = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Affiliate('{self.name}', '{self.speciality}', '{self.city}')"

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
    print(form.speciality.data)
    results = None
    if form.validate():
        print('In validate submit')
        if not form.practice_name.data:
            form.practice_name.data = ''
        if form.speciality.data == 'Choose a Category':
            form.speciality.data = ''
        results = Affiliate.query.filter(Affiliate.name.ilike(f'%{ form.practice_name.data.strip() }%')).filter(Affiliate.speciality.ilike(f'%{ form.speciality.data.strip() }%')).all()[:25]

        json_response = maps.distance_matrix(origins = [form.city_zip.data], destinations = [i.address for i in results], units = 'imperial')
        # 5 10 20 50 75
        print(results)
        pprint(json_response)
        results_filter = []
        for idx, element in enumerate(json_response['rows'][0]['elements']):
            if element['distance']['value'] > int(form.radius.data.split(' ')[0]) * 1760:
                results[idx] = None
        results = [i for i in results if i != None]

        sort_name = request.args.get('sort_name')
        if sort_name == 'A':
            results = results.order_by(Affiliate.name)
        elif sort_name == 'D':
            results = results.order_by(Affiliate.name.desc())
        # results = results.paginate(per_page = 100).items
    print(form.city_zip.errors)
    return render_template('locator.html', underline = 'locator', form = form, results = results)

@app.route("/doctors/")
def doctors():
    form = ProviderForm(request.args, csrf_enabled = False)
    results = None
    if form.validate():
        print('in validate doctors')
        if not form.practice_name.data:
            form.practice_name.data = ''
        if form.speciality.data == 'Choose a Category':
            form.speciality.data = ''
        results = Affiliate.query.filter(Affiliate.name.ilike(f'%{ form.practice_name.data.strip() }%')).filter(Affiliate.speciality.ilike(f'%{ form.speciality.data.strip() }%'))
        results = results.paginate(per_page = 100).items
    return render_template('doctors.html', underline = 'doctors', form = form, doctors = doctors, results = results)

@app.route("/upload-csv/", methods = ["GET", "POST"])
def upload_csv():
    if request.method == 'POST':
        if request.files:
            print(request.files)
            csv_file = request.files['csv_file']
            sec_name = csv_file.filename
            csv_file.save(os.path.join(app.config['UPLOADS'], sec_name))
            with open(os.path.join(app.config['UPLOADS'], sec_name), 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for affiliate in csv_reader:
                    # print(affiliate)
                    db.session.add(Affiliate(**affiliate))
                db.session.commit()
            flash(f"'{sec_name}' uploaded successfully.", 'success')
    return render_template('upload_csv.html')

@app.route("/contact")
def contact():
    return render_template('contact.html', underline = 'contact')

@app.route("/register", methods = ["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.is_doctor.data == 'Yes':
            is_doctor_data = True
        else:
            is_doctor_data = False
        new_user = User(name = form.name.data, email = form.email.data.lower(), password = form.password.data, address = form.address.data, address2 = form.address2.data, city = form.city.data, state = form.state.data, zip_code = form.zip_code.data, is_doctor = is_doctor_data)
        print(new_user)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Hello { new_user.name }! You can log in using your credentials now.', 'success')
        return redirect(url_for('login'))
    else:
        print(form.errors)
        return render_template('signup.html', form = form)

@app.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data.lower()).first()
        if user and user.password == form.password.data:
            login_user(user, remember = form.remember.data)
            flash(f'Welcome { user.name }! You have successfully logged in.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f'You have entered the wrong credentials.', 'danger')
            return redirect(url_for('login'))
    else:
        return render_template('login.html', form = form)

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        flash('You have successfully logged out.', 'success')
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
