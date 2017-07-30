#Email Validation with DB
'''
Create an application that asks a user to enter an email address.
1. If the email address is not valid, have a notification "Email is not valid!" to display on the homepage.
2. Once a valid email address is entered, save to the database the email address the user entered.
3. On the success page, display all the email addresses entered along with the date and the time (e.g. June 24th, 2013, 6:00 PM) when the email addresses were entered

4. (Bonus) add a new feature that allows the user to delete an email record on the success page.
'''

from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
app = Flask(__name__)
app.secret_key = 'secret'
mysql = MySQLConnector(app,'Emails')

@app.route('/')
def index():
    return render_template ('index.html')

@app.route('/email_enter', methods=['POST'])
def create():
    if not EMAIL_REGEX.match(request.form['email']):
        flash('Invalid Email Address')
    else:
        query = "INSERT INTO email (email, created_at, updated_at) VALUES (:email, NOW(), NOW())"
        data = {
            'email': request.form['email']
        }
        mysql.query_db(query, data)
    return redirect('/')

@app.route('/success')
def success():
    emails = mysql.query_db('SELECT email, DATE_FORMAT(created_at, "%c/%d/%y %l:%i%p") AS Entered FROM email')
    print emails
    return render_template ('success.html', all_emails = emails)

@app.route('/delete', methods=['POST'])
def delete():
    query = "DELETE FROM email WHERE email = :email"
    data = {
        'email': request.form['email']
    }
    mysql.query_db(query, data)
    return redirect('/success')

app.run(debug=True)
