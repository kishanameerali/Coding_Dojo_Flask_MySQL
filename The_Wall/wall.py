from flask import Flask, request, redirect, render_template, session, flash
import re
from mysqlconnection import MySQLConnector
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'secret'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
mysql = MySQLConnector(app,'message_wall')

@app.route('/')
def index():
    return render_template ('index.html')

@app.route('/wall')
def message_history():
    msgs = mysql.query_db('SELECT users.first_name, users.last_name, messages.id, messages.message, messages.created_at FROM messages JOIN users ON users.id = messages.user_id ORDER BY messages.created_at DESC')
    return render_template('wall.html', all_msgs = msgs)

@app.route('/post_message', methods=['POST'])
def create():
    query = "INSERT INTO messages (user_id, message, created_at, updated_at) VALUES(:user_id, :message, NOW(), NOW())"
    data = {
        'user_id': session['user_id'],
        'message': request.form['posted_message']
    }
    message_id = mysql.query_db(query, data)
    print message_id
    return redirect('/wall')

@app.route('/post_comment', methods=['POST'])
def respond():
    query = "INSERT INTO comments (message_id, user_id, comment, created_at, updated_at) VALUES (:message_id, :user_id, :comment, NOW(), NOW())"
    data = {
        'message_id': request.form['chosen_msg'],
        'user_id': session['user_id'],
        'comment': request.form['posted_comment']
    }
    mysql.query_db(query, data)
    return redirect('/wall')

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
        query = "SELECT * FROM users WHERE email = :submitted_email"
        data = {
            'submitted_email': request.form['email']
        }
        user_check = mysql.query_db(query, data)
        if len(user_check) > 0:
            flash("That email has already been registered")
            return redirect('/')
        else:
            enc_pw = bcrypt.generate_password_hash(request.form['password'])
            query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:fname, :lname, :email, :pw, NOW(), NOW())"
            data = {
                'fname': request.form['first_name'],
                'lname': request.form['last_name'],
                'email': request.form['email'],
                'pw': enc_pw
            }
            mysql.query_db(query, data)
            #session['user_id'] = user_id
            #print session['user_id']
            flash('You have successfully registered, log in below')
            return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
    data = {
        'email': request.form['email']
    }
    user = mysql.query_db(query, data)
    session['user_id'] = user[0]['id']
    name = user[0]['first_name']
    print session['user_id']
    if bcrypt.check_password_hash(user[0]['password'], request.form['password']):
        return redirect('/wall')
    else:
        flash('Email or password are incorrect')
        return redirect('/')

@app.route('/log_off')
def log_off():
    session.clear()
    return redirect('/')

app.run(debug=True)
