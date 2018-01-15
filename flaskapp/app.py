from flask import Flask, render_template,flash,redirect,url_for,session,logging,request
from flaskext.mysql import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators,SelectField,RadioField,FloatField,SelectMultipleField, widgets
from passlib.hash import sha256_crypt
from functools import wraps
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
app=Flask(__name__)

class MultiCheckboxField(SelectMultipleField):
  widget = widgets.ListWidget(prefix_label=False)
  option_widget = widgets.CheckboxInput()

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
# Config MySQL
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '12345'
app.config['MYSQL_DATABASE_DB'] = 'flaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
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

#init_sql
mysql = MySQL()
mysql.init_app(app)
@app.route('/')
def index():
    return render_template('Home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
# Register Form Class
class RegisterForm(Form):
    first_name = StringField('First Name',[validators.Length(min=1, max=50),validators.DataRequired()])
    middle_name = StringField('Middle Name')
    last_name = StringField('Last Name',[validators.Length(min=1, max=50),validators.DataRequired()])
    npi = StringField('NPI',[validators.DataRequired(),validators.DataRequired()])
    #doctor = SelectField('Doctor',choices=[('a', 'MD/DO'), ('b', 'MBBS'), ('c', 'MBchB'),('d', 'I am not a doctor')])
    #radiologist = RadioField('Radiologist',choices=[('yes', 'Radiologist'), ('no', 'Non Radiologist')])
    training = SelectField('Training', choices=[('staff','Staff'),('r0','Resident-R0/PGY 1'),('r1','Resident-R1/PGY 2'),('r2','Resident-R2/PGY 3'),('r3','Resident-R3/PGY 4'),('r4','Resident-R4/PGY 5')])
    clinical_practice = RadioField('Clinical practice',choices=[('a', '<5 years'),('b', '5-10 years'),('c', '10-15 years'),('d', '15-20 years'),('e', '>20 years')])
    institution_type = RadioField('Institution type',choices=[('private', 'Private practice'), ('academic', 'Academic')])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    clinical_specality = MultiCheckboxField('Clinical Specality', choices=[('Body_Abdomen','Body/Abdomen'),('Head_Neck','Head and Neck'),('Nuclear_Medicine','Nuclear Medicine'),('MSK','MSK'),('Pediatrics','Pediatrics'),('Breast','Breast'),('Chest_Cardiac','Chest/Cardiac'),('Interventional_Radiology','Interventional Radiology'),('ER_General','ER/General')])

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        middle_name = form.middle_name.data
        last_name = form.last_name.data
        npi=form.npi.data
        doctor = request.form['doctor']
        print(doctor)
        session['dummy']=doctor
        #radiologist = form.radiologist.data
        radiologist = request.form['radiologist']
        training = form.training.data
        clinical_practice = form.clinical_practice.data
        clinical_specality = form.clinical_specality.data
        clinical_specality = ''.join(clinical_specality)
        institution_type = form.institution_type.data
        country = request.form['country']
        state = request.form['state']
        email = form.email.data
        token = generate_confirmation_token(email)
        msg = Message('WELCOME TO FLASK', sender = 'sampleapp@gmail.com', recipients = [email])
        msg.body = "Hello Flask message sent from Flask-Mail"
        confirm_url = url_for('confirm_email',token=token,_external=True)
        msg.html = render_template('activate.html',confirm_url=confirm_url)
        mail.send(msg)
        #password = sha256_crypt.encrypt(str(form.password.data))
        #specialization = form.specialization.data

        # Create cursor
        #cur = mysql.get_db().cursor()
        conn = mysql.connect()
        cur =conn.cursor()
        # Execute query
        cur.execute("INSERT INTO USER(first_name,middle_name,last_name,npi,doctor,radiologist,training,clinical_practice,clinical_specality,institution_type,country,state,email) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (first_name,middle_name,last_name,npi,doctor,radiologist,training,clinical_practice,clinical_specality,institution_type,country,state,email))

        # Commit to DB
        conn.commit()

        # Close connection
        cur.close()
        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for("index"))
    return render_template('register.html', form=form)
# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        print(session)
        if 'user_email' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please register and Confrim your email', 'danger')
            return redirect(url_for('register'))
    return wrap
#email conformation
@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email=confirm_token(token)
    except:
        flash('Invalid link','danger')
    else:
        session['user_email']=email
        return redirect(url_for('signup'))

#dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

@app.route('/signup',methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        mail=request.form['email']
        if mail==session['user_email']:
            return render_template('dashboard.html',data=mail)
        else:
            conn = mysql.connect()
            cur =conn.cursor()
            # Execute query
            cur.execute("DELETE FROM USER WHERE email=%s",(session['user_email']))
            # Commit to DB
            conn.commit()
            # Close connection
            cur.close()
            flash("Please Register and get conformation mail to acess Dashboard","danger")
    return render_template('signup.html')


# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

if __name__=='__main__':
    app.secret_key='12345'
    app.run(debug = True)
