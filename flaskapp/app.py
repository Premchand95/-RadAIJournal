from flask import Flask, render_template,flash,redirect,url_for,session,logging,request
from flaskext.mysql import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators,SelectField,RadioField,FloatField,SelectMultipleField, widgets
from passlib.hash import sha256_crypt
from functools import wraps
app=Flask(__name__)

class MultiCheckboxField(SelectMultipleField):
  widget = widgets.ListWidget(prefix_label=False)
  option_widget = widgets.CheckboxInput()

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'flaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
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
    npi = FloatField('NPI',[validators.DataRequired(),validators.DataRequired()])
    doctor = SelectField('Doctor',choices=[('a', 'MD/DO'), ('b', 'MBBS'), ('c', 'MBchB'),('d', 'I am not a doctor')])
    radiologist = RadioField('Radiologist',choices=[('yes', 'Radiologist'), ('no', 'Non Radiologist')])
    training = SelectField('Training', choices=[('staff','Staff'),('r0','Resident-R0/PGY 1'),('r1','Resident-R1/PGY 2'),('r2','Resident-R2/PGY 3'),('r3','Resident-R3/PGY 4'),('r4','Resident-R4/PGY 5')])
    clinical_practice = RadioField('Clinical practice',choices=[('1', '<5 years'),('2', '5-10 years'),('3', '10-15 years'),('4', '15-20 years'),('5', '>20 years')])
    institution_type = RadioField('Institution type',choices=[('1', 'Private practice'), ('0', 'Academic')])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    clinical_specality = MultiCheckboxField('Clinical Specality', choices=[('Body_Abdomen','Body/Abdomen'),('Head_Neck','Head and Neck'),('Nuclear_Medicine','Nuclear Medicine'),('MSK','MSK'),('Pediatrics','Pediatrics'),('Breast','Breast'),('Chest_Cardiac','Chest/Cardiac'),('Interventional_Radiology','Interventional Radiology'),('ER_General','ER/General')])
    #password = PasswordField('Password', [validators.DataRequired(),validators.EqualTo('confirm', message='Passwords do not match')])
    #confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        middle_name = form.middle_name.data
        last_name = form.last_name.data
        npi=form.npi.data
        doctor = form.doctor.data
        radiologist = form.radiologist.data
        training = form.training.data
        clinical_practice = form.clinical_practice.data
        clinical_specality = form.clinical_specality.data
        institution_type = form.institution_type.data
        country = request.form['country']
        state = request.form['state']
        email = form.email.data
        #password = sha256_crypt.encrypt(str(form.password.data))
        #specialization = form.specialization.data

        # Create cursor
        cursor = mysql.get_db().cursor()

        # Execute query
        cur.execute("INSERT INTO USERS(first_name,middle_name,last_name,npi,doctor,radiologist,training,clinical_practice,clinical_specality,institution_type,country,state,email) VALUES(%s, %s, %s,%f, %s,%s,%s,%s, %s, %s, %s,%s,%s)", (first_name,middle_name,last_name,npi,doctor,radiologist,training,clinical_practice,clinical_specality,institution_type,country,state,email))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('index'))
    return render_template('register.html', form=form)
# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result= cur.execute("SELECT * FROM USERS WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']
            name=data['name']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                session['name']=name
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Incorrect Password'
                return render_template('login.html', error=error)
                # Close connection
            cur.close()
        else:
            error = 'User not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


#dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

if __name__=='__main__':
    app.secret_key='12345'
    app.run(debug=True)
