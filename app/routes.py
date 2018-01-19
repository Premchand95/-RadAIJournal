#!/bin/python

import os
import pandas as pd
from datetime import datetime
from flask import Flask, render_template,Blueprint,flash,redirect,url_for,send_from_directory,session,logging,request
#from wtforms import Form, StringField, TextAreaField, PasswordField, validators,SelectField,RadioField,FloatField,SelectMultipleField, widgets
from passlib.hash import sha256_crypt
from functools import wraps
from flask_mail import Mail,Message
from itsdangerous import URLSafeTimedSerializer
from flask_bootstrap import __version__ as FLASK_BOOTSRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from sqlalchemy import update
from flask_wtf import FlaskForm
from markupsafe import escape
from wtforms import StringField,IntegerField, PasswordField, TextAreaField, validators, BooleanField, SubmitField, RadioField, SelectMultipleField, TextField, SelectField, FloatField, widgets
from wtforms.validators import DataRequired, Length , EqualTo , Email

from PIL import Image
from io import StringIO

from app import app, db
from app.forms import LoginForm, XrayForm, RegisterForm
from app.models import User, Report


#config Mail
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_SALT'] = 'super_secret'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'avanigaddaprem@gmail.com'
app.config['MAIL_PASSWORD'] = 'Prem@1995'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail =Mail(app)

mydata = pd.read_csv('app/static/FinalWorklist.csv')
mydata['img_index'] = mydata['img']
mydata.set_index('img_index',inplace=True)

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class RegForm(FlaskForm):
    first_name = StringField('First Name',[validators.Length(min=1, max=50),validators.DataRequired()])
    middle_name = StringField('Middle Name')
    last_name = StringField('Last Name',[validators.Length(min=1, max=50),validators.DataRequired()])
    npi=StringField('NPI', [validators.Length(min=1, max=10)])
    doctor = SelectField('Doctor',choices=[('a', 'MD/DO'), ('b', 'MBBS'), ('c', 'MBchB'),('d', 'I am not a doctor')])
    radiologist = RadioField('Radiologist',choices=[('yes', 'Radiologist'), ('no', 'Non Radiologist')])
    training = SelectField('Training', choices=[('staff','Staff'),('r0','Resident-R0/PGY 1'),('r1','Resident-R1/PGY 2'),('r2','Resident-R2/PGY 3'),('r3','Resident-R3/PGY 4'),('r4','Resident-R4/PGY 5')])
    clinical_practice = RadioField('Clinical practice',choices=[('a', '<5 years'),('b', '5-10 years'),('c', '10-15 years'),('d', '15-20 years'),('e', '>20 years')])
    clinical_specality = MultiCheckboxField('Clinical Specality', choices=[('Body_Abdomen','Body/Abdomen'),('Head_Neck','Head and Neck'),('Nuclear_Medicine','Nuclear Medicine'),('MSK','MSK'),('Pediatrics','Pediatrics'),('Breast','Breast'),('Chest_Cardiac','Chest/Cardiac'),('Interventional_Radiology','Interventional Radiology'),('ER_General','ER/General')])
    institution_type = RadioField('Institution type',choices=[('private', 'Private practice'), ('academic', 'Academic')])
    submit = SubmitField('submit')


class UserProfile(db.Model):
    profile_id = db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String(160))
    middle_name = db.Column(db.String(160))
    last_name = db.Column(db.String(160))
    npi = db.Column(db.Integer,unique=True)
    doctor = db.Column(db.String(32))
    radiologist = db.Column(db.String(32))
    training = db.Column(db.String(32))
    clinical_practice = db.Column(db.String(32))
    clinical_specality = db.Column(db.String(32))
    institution_type = db.Column(db.String(32))
    country = db.Column(db.String(32))
    state = db.Column(db.String(32))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)

#mail classes
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        print(session)
        if 'login_user' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please register and Confrim your email', 'danger')
            return redirect(url_for('register'))
    return wrap

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title= 'Nyumbani')

@app.route('/worklist')
@is_logged_in
def worklist():
    #search the DB for all studies read by the current user
    reports = Report.query.filter_by(user_id=current_user.id)
    reports_count = reports.count()
    cxr_read = []

    #are there any images returned
    if reports_count > 0:
        for report in reports:
            cxr_read.append(report.img_id)

        # Drop them from the dataframe before sampling them again to create the worklist
        unread_cxr = mydata.drop(cxr_read)

    else:
        unread_cxr = mydata

    #sample 20 studies from the list
    myworklist = unread_cxr.sample(20)

    myworklist_data = []
    for index,row in myworklist.iterrows():
        mydict = {
            "img":row.img,
            "pt_id":row.pt_id,
            "study": "CXR",
            "age":row.age,
            "sex":row.sex
        }

        myworklist_data.append(mydict)

    return render_template('worklist.html',myworklist_data=myworklist_data)

@app.route('/worklist2')
@is_logged_in
def worklist2():
    #search the DB for all studies read by the current user

    reports = Report.query.filter_by(user_id=current_user.id)
    cxr_read = []

    #are there any images returned
    if reports.count > 0:
        for report in reports:
            cxr_read.append(report.img_id)

        # Drop them from the dataframe before sampling them again to create the worklist
        unread_cxr = mydata.drop(cxr_read)

    else:
        unread_cxr = mydata

    #sample 20 studies from the list
    myworklist = unread_cxr.sample(20)

    myworklist_data = []
    for index,row in myworklist.iterrows():
        mydict = {
            "img":row.img,
            "pt_id":row.pt_id,
            "study": "CXR",
            "age":row.age,
            "sex":row.sex
        }

        myworklist_data.append(mydict)

    return render_template('worklist.html',myworklist_data=myworklist_data)

@app.route('/stats')
@is_logged_in
def stats():
    return render_template('stats.html')

@app.route('/study/<img_id>',methods=['GET','POST'])
@is_logged_in
def study(img_id):
    form = XrayForm()
    if request.method == 'GET':

        file_name = 'cxr/' + str(img_id)

        #search for patient ID, Age and sex for the specific image we are rendering
        img_data = mydata.loc[mydata['img'] == img_id]
        if len(img_data) > 0:
            #means there are metadata for that image
            for index,row in img_data.iterrows():
                img_details = {
                    'pt_id' : row.pt_id,
                    'age' : row.age,
                    'sex' : row.sex
                }
        return render_template('study.html',user_image = file_name, image_details = img_details,img_id = img_id, form=form)
    elif request.method == 'POST':
        #validate that the forms data is correct
        # Pneumonia must be selected
        if request.form.get('pneumonia'):
            _pneumonia = request.form.get('pneumonia')
        else:
            #pneumonia field was not selected
            flash("Pneumonia diagnosis must be selected !",category="danger")
            return redirect(url_for('study',img_id = img_id))

        #now we have pneumonia we can check if other fields are present and save them
        if request.form.get('infiltrates'):
            infiltrates = request.form.get('infiltrates')
        else:
            infiltrates = '0'

        if request.form.get('consolidation'):
            consolidation = request.form.get('consolidation')
        else:
            consolidation = '0'

        if request.form.get('atelectasis'):
            atelectasis = request.form.get('atelectasis')
        else:
            atelectasis = '0'

        if request.form.get('comments'):
            comments = request.form.get('comments')
        else:
            comments = ''

        #get the ground truth and prediction for the img
        img_data = mydata.loc[mydata['img'] == img_id]
        if len(img_data) > 0:
            #means there are metadata for that image
            for index,row in img_data.iterrows():
                ground_truth = row.Pneumonia,
                prediction = row.Pneumonia_pred

        #save our cxr report
        try:
            report = Report(img_id = img_id, pneumonia = _pneumonia, consolidation=consolidation,
            infiltrates=infiltrates, atelectasis=atelectasis, comments=comments, user_id=current_user.id,
            ground_truth = ground_truth, prediction = prediction)

            db.session.add(report)
            db.session.commit()
            flash("Report saved successfully!", 'success')
        except:
            flash("CXR report was NOT saved successfully","danger")
            return redirect(url_for('study',img_id = img_id))

        return redirect(url_for('worklist'))

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("Invalid user",'danger')
            return redirect(url_for('login'))
        if user.confrim=='NO':
            flash('unconfrimed account, Please check your mail to confrim',category='danger')
            return redirect(url_for('login'))
        if not user.check_password(form.password.data):
            flash("Invalid password",'danger')
            return redirect(url_for('login'))
        login_user(user, remember = form.remember_me.data)
        next_page = request.args.get('next')
        session['login_user']=True
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('profile'))
    return render_template("login.html",title="Sign In", form=form)

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        email = user.email
        token = generate_confirmation_token(email)
        msg = Message('WELCOME TO FLASK', sender = 'sampleapp@gmail.com', recipients = [email])
        msg.body = "Hello Flask message sent from Flask-Mail"
        confirm_url = url_for('confirm_email',token=token,_external=True)
        msg.html = render_template('activate.html',confirm_url=confirm_url)
        mail.send(msg)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!','success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# User Register
@app.route('/profile', methods=['GET', 'POST'])
@is_logged_in
def profile():
    form=RegForm(request.form)
    if form.validate_on_submit():
        first_name = form.first_name.data
        userProfile=UserProfile(first_name=first_name)
        middle_name = form.middle_name.data
        userProfile=UserProfile(middle_name=middle_name)
        last_name = form.last_name.data
        userProfile=UserProfile(last_name=last_name)
        npi=int(form.npi.data)
        userProfile=UserProfile(npi=npi)
        doctor=form.doctor.data
        userProfile=UserProfile(doctor=doctor)
        radiologist=form.radiologist.data
        userProfile=UserProfile(radiologist=radiologist)
        training=form.training.data
        userProfile=UserProfile(training=training)
        clinical_practice=form.clinical_practice.data
        userProfile=UserProfile(clinical_practice=clinical_practice)
        clinical_specality=form.clinical_specality.data
        clinical_specality = ''.join(clinical_specality)
        userProfile=UserProfile(clinical_specality=clinical_specality)
        institution_type=form.institution_type.data
        userProfile=UserProfile(institution_type=institution_type)
        db.session.add(userProfile)
        db.session.commit()
        return render_template('worklist.html', form=form)
    return render_template('profile.html', form=form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
#email conformation
@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email=confirm_token(token)
    except:
        flash('Invalid link','danger')
    else:
        user = User.query.filter_by(email=email).first()
        user.confrim = 'YES'
        db.session.commit()
        session['user_email']=email
        return redirect(url_for('login'))
