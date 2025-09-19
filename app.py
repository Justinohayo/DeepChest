from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages and sessions

# Database connection config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'test1234',
    'database': 'DeepChest'
}

@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('index.html', username=session.get('username'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM login WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            # Set session variables
            session['user_id'] = user['USERID']
            session['username'] = user['username']
            session['userType'] = user['userType']
            session['clinicID'] = user['clinicID']

            # Redirect based on user type
            if user['userType'] == 'patient':
                return redirect(url_for('patient_home'))
            elif user['userType'] == 'doctor':
                return redirect(url_for('doctor_home'))
            elif user['userType'] == 'clinicadmin':
                return redirect(url_for('admin_home'))
            else:
                flash('Unknown user type')
                return redirect(url_for('login'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template('login.html')

# Add these routes for different user homepages
@app.route('/patient_home')
def patient_home():
    if session.get('userType') == 'patient':
        return render_template('/patient/patienthome.html', username=session.get('username'))
    return redirect(url_for('login'))

@app.route('/doctor_home')
def doctor_home():
    if session.get('userType') == 'doctor':
        return render_template('/doctor/doctorhome.html', username=session.get('username'))
    return redirect(url_for('login'))

@app.route('/admin_home')
def admin_home():
    if session.get('userType') == 'clinicadmin':
        return render_template('/clinic_admin/adminhome.html', username=session.get('username'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        # Add user registration logic here
        return redirect(url_for('home'))
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
