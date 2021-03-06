from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, validators, BooleanField, SubmitField, RadioField, SelectMultipleField, TextField, SelectField, FloatField, widgets
from wtforms.validators import DataRequired, Length , EqualTo , Email

from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email address',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    confrim = StringField('confrim')
    submit = SubmitField('Sign In')

class XrayForm(FlaskForm):
    pneumonia = StringField('Pneumonia Diagnosis',validators=[DataRequired()])
    consolidation = StringField('Consolidation')
    infiltrates = StringField('Infiltrates')
    atelectasis = StringField('Atelectasis')
    comments = TextField('Comments')
    submit = SubmitField('Save Report')

'''
class ProfileForm(FlaskForm):
    first_name = StringField('First Name',[validators.Length(min=1, max=50),validators.DataRequired()])
    middle_name = StringField('Middle Name')
    last_name = StringField('Last Name',[validators.Length(min=1, max=50),validators.DataRequired()])
    npi = StringField('NPI',[validators.Length(min=0 , max=10),validators.DataRequired()])
    doctor = SelectField('Doctor',choices=[('MD/DO', 'MD/DO'), ('MBBS', 'MBBS'), ('MBchB', 'MBchB'),('Not_doctor', 'I am not a doctor')])
    radiologist = RadioField('Radiologist',choices=[('yes', 'Radiologist'), ('no', 'Non Radiologist')])
    training = SelectField('Training', choices=[('staff','Staff'),('r0','Resident-R0/PGY 1'),('r1','Resident-R1/PGY 2'),('r2','Resident-R2/PGY 3'),('r3','Resident-R3/PGY 4'),('r4','Resident-R4/PGY 5')])
    clinical_practice = SelectField('Clinical practice',choices=[('0-5', '<5 years'),('5-10', '5-10 years'),('10-15', '10-15 years'),('15-20', '15-20 years'),('20+', '>20 years')])
    institution_type = SelectField('Institution type',choices=[('private', 'Private practice'), ('academic', 'Academic')])
    clinical_specialty = MultiCheckboxField('Clinical Specality', choices=[('Body_Abdomen','Body/Abdomen'),('Head_Neck','Head and Neck'),('Nuclear_Medicine','Nuclear Medicine'),('MSK','MSK'),('Pediatrics','Pediatrics'),('Breast','Breast'),('Chest_Cardiac','Chest/Cardiac'),('Interventional_Radiology','Interventional Radiology'),('ER_General','ER/General')])
    country = SelectField('country')
    state = SelectField('state')
'''
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
