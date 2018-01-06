from flask import Flask, render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators,SelectField
from passlib.hash import sha256_crypt
from functools import wraps
app=Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'flaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#init_sql
mysql = MySQL(app)

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
    name = StringField('Name',[validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    specialization = SelectField('specialization',choices=[('B', 'Breast'), ('PC', 'Chest/cardio'), ('I', 'IR'),('EG', 'ER/General'),('BAM', 'Body/abdomen/MRI'),('HN', 'Head/Neck')])
    experience = SelectField('experience', choices=[('0','R0'),('1','R1'),('2','R2'),('3','R3')])

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        specialization = form.specialization.data
        experience = form.experience.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO USERS(name, email, username, password,specialization,experience) VALUES(%s, %s, %s, %s,%s,%s)", (name, email, username, password,specialization,experience))

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
