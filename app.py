from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import webbrowser

app = Flask(__name__)
app.secret_key = '1234'  # Needed for flash messages and sessions

# Database connection config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',
    'database': 'DeepChest'
}

# Configures Route for the home page
@app.route('/')
def home():
    return render_template('index.html', username=session.get('username'))

# Configures Route for the login page 
@app.route('/login', methods=['GET', 'POST'])
#function to handle login logic such as verifying user credentials and redirecting based on user type
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        # Query to check if user exists
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
                  conn = mysql.connector.connect(**db_config)
                  cursor = conn.cursor(dictionary=True)
                  cursor.execute("SELECT firstName, lastName FROM patient WHERE USERID = %s", (user['USERID'],))
                  patient = cursor.fetchone()
                  cursor.close()
                  conn.close()
                  if patient:
                      session['firstName'] = patient['firstName']
                      session['lastName'] = patient['lastName']
                  else:
                      session['firstName'] = user['username']
                      session['lastName'] = ""
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

#Route for signing up new users(Incomplete, just a placeholder)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    import mysql.connector
    clinics = []
    doctors = []
    if request.method == 'POST':
        # Get form data
        clinicID = request.form.get('clinicID')
        doctorID = request.form.get('doctorID')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        phoneNumber = request.form.get('phoneNumber')
        password = request.form.get('password')
        birthday = request.form.get('birthday')
        address = request.form.get('address')
        city = request.form.get('city')
        province = request.form.get('province')
        postalCode = request.form.get('postalCode')
        insurance = request.form.get('insurance')
        username = email  # Or generate a username as needed
        childID = None  # Assuming childID is optional or can be set later

        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert into login table (assuming userType is 'patient')
        cursor.execute(
            "INSERT INTO login (USERID, username, password, userType, clinicID) VALUES (%s, %s, %s, %s, %s)",
            (None, username, password, 'patient', clinicID)
        )
        # Get the USERID of the newly inserted user
        conn.commit()
        cursor.execute("SELECT USERID FROM login WHERE username=%s", (username,))
        user = cursor.fetchone()
        user_id = user[0] if user else None

        # Insert into patient table (if you have one)
        # Uncomment and adjust the following if you have a patient table:
        cursor.execute(
           "INSERT INTO `patient` (`firstName`, `lastName`,`dateofbirth`, `USERID`, `address`, `city`, `province`, `postalCode`, `phone`, `email`,`insurance`,`doctorID`,`childID`,`clinicID`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)",
            (firstName, lastName, birthday, user_id, address, city, province, postalCode, phoneNumber, email, insurance, doctorID, childID, clinicID)
         )

        conn.commit()
        cursor.close()
        conn.close()

        flash('Account created successfully! Please log in.')
        return redirect(url_for('login'))
    else:
        # Fetch clinics from the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT clinicID, city, province FROM clinic")
        clinics = cursor.fetchall()
        # Fetch doctors from the database
        cursor.execute("SELECT USERID, firstName, lastName, clinicID FROM doctor")
        doctors = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('signup.html', clinics=clinics, doctors=doctors)


#Routes for each of the user types to their respective home pages. Used above in login route
@app.route('/patient_home')
def patient_home():
    if session.get('userType') == 'patient':
        return render_template(
            'patient/patienthome.html',
            firstName=session.get('firstName'),
            lastName=session.get('lastName'),
            user_id=session.get('user_id')
        )
    return redirect(url_for('login'))

# Doctor Home Page
@app.route('/doctor_home')
def doctor_home():
    if session.get('userType') == 'doctor':
        return render_template('doctor/doctorhome.html', username=session.get('username'))
    return redirect(url_for('login'))

# Doctor Appointments Page
@app.route('/doctor/appointments')
def doctor_appointments():
    if session.get('userType') == 'doctor':
        return render_template('doctor/doctor_appointments.html', username=session.get('username'))
    return redirect(url_for('login'))

# Doctor Patients Page
@app.route('/doctor/patients')
def doctor_patients():
    if session.get('userType') == 'doctor':
        return render_template('doctor/doctor_patients.html', username=session.get('username'))
    return redirect(url_for('login'))

# Doctor Reports Page
@app.route('/doctor/reports')
def doctor_reports():
    if session.get('userType') == 'doctor':
        return render_template('doctor/doctor_reports.html', username=session.get('username'))
    return redirect(url_for('login'))

# Doctor AI Diagnosis Page
@app.route('/doctor/ai_diagnosis')
def doctor_ai_diagnosis():
    if session.get('userType') == 'doctor':
        return render_template('doctor/doctor_ai_diagnosis.html', username=session.get('username'))
    return redirect(url_for('login'))

# Doctor Account Page
@app.route('/doctor/account')
def doctor_account():
    if session.get('userType') == 'doctor':
        return render_template('doctor/doctor_account.html', username=session.get('username'))
    return redirect(url_for('login'))




# Clinic Admin Home Page
@app.route('/admin_home')
def admin_home():
    if session.get('userType') == 'clinicadmin':
        return render_template('/clinic_admin/adminhome.html', username=session.get('username'))
    return redirect(url_for('login'))

# Patient Appointments Page
@app.route('/patient/appointments')
def patient_appointments():
    if session.get('userType') == 'patient':
        return render_template(
            'patient/p_appointments.html',
            user_id=session.get('user_id')
        )
    return redirect(url_for('login'))

# Patient Reports Page
@app.route('/patient/reports')
def patient_reports():
    if session.get('userType') == 'patient':
        return render_template(
            'patient/myreports.html',
            user_id=session.get('user_id')
        )
    return redirect(url_for('login'))

# Patient Messages Page
@app.route('/patient/messages')
def patient_messages():
    if session.get('userType') == 'patient':
        return render_template(
            'patient/messages.html',
            user_id=session.get('user_id')
        )
    return redirect(url_for('login'))

# Patient Notifications Page
@app.route('/patient/notifications')
def patient_notifications():
    if session.get('userType') == 'patient':
        return render_template(
            'patient/notifications.html',
            user_id=session.get('user_id')
        )
    return redirect(url_for('login'))

# Patient Manage Account Page
@app.route('/patient/account')
def patient_account():
    if session.get('userType') == 'patient':
        return render_template(
            'patient/p_modifyaccount.html',
            user_id=session.get('user_id')
        )
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)