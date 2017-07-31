#Login and Registration
'''
The user inputs their information, we verify that the information is correct, insert it into the database and return back with a success message. If the information is not valid, redirect to the registration page and show the following requirements:

Validations and Fields to Include

First Name - letters only, at least 2 characters and that it was submitted
Last Name - letters only, at least 2 characters and that it was submitted
Email - Valid Email format, and that it was submitted
Password - at least 8 characters, and that it was submitted
Password Confirmation - matches password

Create a basic login and registration
 Redirect user to a success page on successful login or register
 Display error messages for either log in or registration if validations fail
 Use Bcrypt to hash passwords before inserting them into the database
'''

from flask import Flask, request, redirect, render_template, session, flash
import re
from mysqlconnection import MySQLConnector
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'secret'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
mysql = MySQLConnector(app,'login_registration')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registered', methods=['POST'])
def registered():
    error_messages = []

    if len(request.form['first_name']) < 2:
        error_messages.append("First Name must be 2 characters minimum")

    if (request.form['first_name']).isalpha() == False:
        error_messages.append("First Name can only contain letters")

    if len(request.form['last_name']) < 2:
        error_messages.append("Last Name must be 2 characters minimum")

    if (request.form['last_name']).isalpha() == False:
        error_messages.append("Last Name can only contain letters")

    if not EMAIL_REGEX.match(request.form['email']):
        error_messages.append("Invalid email address")

    if len(request.form['password']) < 8:
        error_messages.append("Password must be 8 characters minimum")

    if request.form['password'] != request.form['confirm_password']:
        error_messages.append("Password and confirmation don't match")

    if(error_messages):
        for error in error_messages:
            flash(error)
        return redirect('/')
    else:
        query = "SELECT * FROM registered_users WHERE email = :submitted_email"
        data = {
            'submitted_email': request.form['email']
        }
        user_check = mysql.query_db(query, data)
        if len(user_check) > 0:
            flash("That email has already been registered")
            return redirect('/')
        else:
            enc_pw = bcrypt.generate_password_hash(request.form['password'])
            query = "INSERT INTO registered_users (first_name, last_name, email, password, created_at, updated_at) VALUES (:fname, :lname, :email, :pw, NOW(), NOW())"
            data = {
                'fname': request.form['first_name'],
                'lname': request.form['last_name'],
                'email': request.form['email'],
                'pw': enc_pw
            }
            user_id = mysql.query_db(query, data)
            session['user_id'] = user_id
            print session['user_id']
            new_user_query = 'SELECT * FROM registered_users WHERE id = :id'
            new_user_data = {
                'id': session['user_id']
            }
            new_user = mysql.query_db(new_user_query, new_user_data)
            return render_template('reg_complete.html', new_user_info = new_user)

@app.route('/login', methods=['POST'])
def login():
    query = "SELECT * FROM registered_users WHERE registered_users.email = :email LIMIT 1"
    data = {
        'email': request.form['email']
    }
    user = mysql.query_db(query, data)
    #session['user_id'] = user['id']
    #print session['user_id']
    if bcrypt.check_password_hash(user[0]['password'], request.form['password']):
        return render_template('profile.html', user_info = user)
    else:
        flash('Email or password are incorrect')
        return redirect('/')

app.run(debug=True)
