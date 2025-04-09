from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3 
import subprocess
from Registration import register_user, login_user
from RideManagement import save_ride, search_rides  # Import ride management functions

app = Flask(__name__)

# Set a secret key for session management (Change this to a secure, random string)
app.secret_key = 'your_secret_key_here'

# Function to create the database if it doesn't exist
def create_database():
    print("inside db")
    if not os.path.exists('user_data.db'):
        subprocess.run(['python', 'DBScript.py'])

@app.route('/')
def first_page():
    return render_template('first.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form.get("firstName")
        lastname = request.form.get("lastName")
        contactno = request.form.get("contactNumber")
        emailid = request.form.get("emailid")
        password = request.form.get("password")
        cnfpassword = request.form.get("confirmPassword")

        if password != cnfpassword:
            return render_template('signup.html', message="Passwords do not match.")

        create_database()
        try:
            register_user(firstname, lastname, contactno, emailid, password)
            return redirect(url_for('login_form'))
        except sqlite3.IntegrityError:
            return render_template('signup.html', message="Email already exists.")

    return render_template('signup.html')

    

@app.route('/login', methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        email = request.form.get("emailid")
        password = request.form.get("password")
        login_result = login_user(email, password)

        if 'Welcome' in login_result:
            session['username'] = email  # Store logged-in user in session
            return redirect(url_for('home'))  # Redirect to offer ride page after login
        else:
            return render_template('login.html', message="Invalid password, try again.")

    return render_template('login.html')
@app.route('/home')
def home():
    return render_template('home.html')  # Ensure home.html exists


@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear session
    return redirect(url_for('/'))

@app.route('/offer', methods=['GET', 'POST'])
def offer_ride():
    if 'username' not in session:
        return redirect(url_for('login_form'))  # Redirect to login if not logged in

    if request.method == 'POST':
        from_place = request.form.get("from")
        to_place = request.form.get("to")
        via = request.form.get("via")
        seats = request.form.get("seats")
        date = request.form.get("date")
        time = request.form.get("time")
        vehno =request.form.get("vehno")
        username=session['username']
        # Save ride information to the database
        ride_giver_name= username  # Replace with actual user name from session or database
        save_ride(ride_giver_name, from_place, to_place, via, seats, date, time,vehno)

        return render_template('offer.html', message="Ride offered successfully!", username=session['username'])

    return render_template('offer.html', username=session['username'])  # Pass username to HTML

@app.route('/find', methods=['GET', 'POST'])
def find_rides():
    if 'username' not in session:
        return redirect(url_for('login_form'))  # Redirect to login if not logged in

    if request.method == 'POST':
        from_place = request.form.get("from")
        to_place = request.form.get("to")
        find_date = request.form.get("date")
        find_time = request.form.get("time")
        
        rides = search_rides(from_place, to_place, find_date, find_time)
        print(rides)
        return render_template('matchingride.html', rides=rides, username=session['username'])

    return render_template('find.html', username=session['username'])

@app.route('/profile', methods=['GET', 'POST'])
def profile():  
    if 'username' not in session:
        return redirect(url_for('login_form'))

    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name, contact_number, emailid FROM users WHERE emailid = ?", (session['username'],))
    user = cursor.fetchone()

    if request.method == 'POST':
        firstname = request.form.get("first_name")
        lastname = request.form.get("last_name")
        contactno = request.form.get("contact_number")

        cursor.execute("""
            UPDATE users
            SET first_name = ?, last_name = ?, contact_number = ?
            WHERE emailid = ?
        """, (firstname, lastname, contactno, session['username']))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))

    conn.close()
    return render_template('profile.html', user=user)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)