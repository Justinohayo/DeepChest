from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import webbrowser
import calendar
import re
from datetime import date, datetime

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
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT firstName, lastName FROM doctor WHERE USERID = %s", (user['USERID'],))
                doctor = cursor.fetchone()
                cursor.close()
                conn.close()
                session['firstName'] = doctor['firstName']
                session['lastName'] =  doctor['lastName']
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

# Patient Appointments Page
@app.route('/patient/appointments')
def patient_appointments():
    if session.get('userType') != 'patient':
        return redirect(url_for('login'))
    user_id = session.get('user_id')

    # Fetch all appointments for this patient
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.appointment_date, a.appointment_time, d.firstName AS doctorFirstName, d.lastName AS doctorLastName, a.symptoms
        FROM appointments a
        JOIN doctor d ON a.doctorID = d.USERID
        WHERE a.patientID = %s
        ORDER BY a.appointment_date, a.appointment_time
    """, (user_id,))
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'patient/p_appointments.html',
        appointments=appointments
    )

# Patient Reports Page
@app.route('/patient/reports')
def patient_reports():
    if session.get('userType') == 'patient':
        user_id = session.get('user_id')
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.reportID, r.reportDate, r.doctorID,
                   d.firstName AS doctorFirstName, d.lastName AS doctorLastName
            FROM Reports r
            JOIN doctor d ON r.doctorID = d.USERID
            WHERE r.patientID = %s
            ORDER BY r.reportDate DESC
        """, (user_id,))
        reports = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template(
            'patient/myreports.html',
            user_id=user_id,
            reports=reports
        )
    return redirect(url_for('login'))

@app.route('/patient/search_reports', methods=['GET'])
def search_reports():
    if session.get('userType') != 'patient':
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    query = request.args.get('query', '').strip()

    # Month name support
    month_map = {month.lower(): index for index, month in enumerate(calendar.month_name) if month}
    query_lower = query.lower()
    month_num = None
    year_num = None
    for name, num in month_map.items():
        if name in query_lower:
            month_num = num
            match = re.search(rf"{name}\s+(\d{{4}})", query_lower)
            if match:
                year_num = int(match.group(1))
            else:
                match = re.search(rf"(\d{{4}})\s+{name}", query_lower)
                if match:
                    year_num = int(match.group(1))
            break

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    if month_num and year_num:
        cursor.execute("""
            SELECT r.reportID, r.reportDate, r.doctorID,
                   d.firstName AS doctorFirstName, d.lastName AS doctorLastName
            FROM Reports r
            JOIN doctor d ON r.doctorID = d.USERID
            WHERE r.patientID = %s AND MONTH(r.reportDate) = %s AND YEAR(r.reportDate) = %s
            ORDER BY r.reportDate DESC
        """, (user_id, month_num, year_num))
    elif month_num:
        cursor.execute("""
            SELECT r.reportID, r.reportDate, r.doctorID,
                   d.firstName AS doctorFirstName, d.lastName AS doctorLastName
            FROM Reports r
            JOIN doctor d ON r.doctorID = d.USERID
            WHERE r.patientID = %s AND MONTH(r.reportDate) = %s
            ORDER BY r.reportDate DESC
        """, (user_id, month_num))
    else:
        cursor.execute("""
            SELECT r.reportID, r.reportDate, r.doctorID,
                   d.firstName AS doctorFirstName, d.lastName AS doctorLastName
            FROM Reports r
            JOIN doctor d ON r.doctorID = d.USERID
            WHERE r.patientID = %s AND (
                CAST(r.reportID AS CHAR) LIKE %s
                OR r.reportDate LIKE %s
                OR d.firstName LIKE %s
                OR d.lastName LIKE %s
            )
            ORDER BY r.reportDate DESC
        """, (user_id, f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
    reports = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template(
        'patient/myreports.html',
        user_id=user_id,
        reports=reports
    )

# Report details page for patients
@app.route('/patient/report_details')
def patient_report_details():
    if session.get('userType') != 'patient':
        return redirect(url_for('login'))
    report_id = request.args.get('reportID')
    user_id = session.get('user_id')
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, d.firstName AS doctorFirstName, d.lastName AS doctorLastName
        FROM Reports r
        JOIN doctor d ON r.doctorID = d.USERID
        WHERE r.reportID = %s AND r.patientID = %s
    """, (report_id, user_id))
    report = cursor.fetchone()
    cursor.close()
    conn.close()
    if not report:
        flash("Report not found.", "danger")
        return redirect(url_for('patient_reports'))
    return render_template('patient/reportdetails.html', report=report)

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


# Patient Manage Account Page (GET: pre-fill, POST: update)
@app.route('/patient/account', methods=['GET', 'POST'])
def patient_account():
    if session.get('userType') != 'patient':
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        # Get updated form data
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
        # Update patient table
        cursor.execute("""
            UPDATE patient SET firstName=%s, lastName=%s, dateofbirth=%s, address=%s, city=%s, province=%s, postalCode=%s, phone=%s, email=%s, insurance=%s WHERE USERID=%s
        """, (firstName, lastName, birthday, address, city, province, postalCode, phoneNumber, email, insurance, user_id))
        # Update login table (password and email/username)
        cursor.execute("""
            UPDATE login SET username=%s, password=%s WHERE USERID=%s
        """, (email, password, user_id))
        conn.commit()
        flash('Account updated successfully!')
        # Re-fetch updated info for display
    cursor.execute("SELECT * FROM patient WHERE USERID = %s", (user_id,))
    patient = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('patient/p_modifyaccount.html', patient=patient)

# Add Child Page for Patient
@app.route('/patient/add-child', methods=['GET', 'POST'])
def add_child():
    if session.get('userType') != 'patient':
        return redirect(url_for('login'))
    # You can add POST logic here to handle child registration
    return render_template('patient/add-child.html')


# Doctor Home Page
@app.route('/doctor_home')
def doctor_home():
    if session.get('userType') == 'doctor':
        return render_template('doctor/doctorhome.html', firstName=session.get('firstName'), lastName=session.get('lastName'))
    return redirect(url_for('login'))

# Doctor Appointments Page
# Doctor Appointments List
@app.route('/doctor/appointments')
def doctor_appointments():
    if session.get('userType') != 'doctor':
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Join appointments with patient info
    cursor.execute("""
        SELECT a.apptID, a.appointment_date, a.appointment_time, a.symptoms,
               p.firstName, p.lastName
        FROM appointments a
        JOIN patient p ON a.patientID = p.USERID
        ORDER BY a.appointment_date, a.appointment_time
    """)
    appointments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('doctor/doctor_appointments.html',
                           appointments=appointments,
                           username=session.get('username'))


# Doctor Appointment Detail Page
@app.route('/doctor/appointments/detail')
def doctor_appointments_detail():
    if session.get('userType') != 'doctor':
        return redirect(url_for('login'))

    apptID = request.args.get('apptID')
    if not apptID:
        flash("No appointment selected.")
        return redirect(url_for('doctor_appointments'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Get full appointment + patient info
    cursor.execute("""
        SELECT a.apptID, a.appointment_date, a.appointment_time, a.symptoms,
               p.firstName, p.lastName, p.dateofbirth, p.phone, p.email
        FROM appointments a
        JOIN patient p ON a.patientID = p.USERID
        WHERE a.apptID = %s
    """, (apptID,))
    appointment = cursor.fetchone()

    cursor.close()
    conn.close()

    if not appointment:
        flash("Appointment not found.")
        return redirect(url_for('doctor_appointments'))

    return render_template('doctor/doctor_appointment_detail.html',
                           appointment=appointment,
                           username=session.get('username'))

# Doctor Patients Page
@app.route('/doctor/patients')
def doctor_patients():
    if session.get('userType') == 'doctor':
        return render_template('doctor/doctor_patients.html', username=session.get('username'))
    return redirect(url_for('login'))

# Doctor Reports Page
#@app.route('/doctor/reports')
#def doctor_reports():
 #   if session.get('userType') == 'doctor':
  #      return render_template('doctor/doctor_reports.html', username=session.get('username'))
  #  return redirect(url_for('login'))

# Doctor Reports Page
# Doctor Reports Page
@app.route('/doctor/reports')
def doctor_reports():
    if session.get('userType') != 'doctor':
        return redirect(url_for('login'))

    doctor_id = session.get('user_id')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Pull all reports for this doctor, join patient info
    cursor.execute("""
        SELECT r.reportID, r.files, p.firstName, p.lastName
        FROM Reports r
        JOIN patient p ON r.patientID = p.USERID
        WHERE r.doctorID = %s
    """, (doctor_id,))

    reports = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'doctor/doctor_reports.html',
        username=session.get('username'),
        reports=reports
    )


# Doctor AI Diagnosis Page
@app.route('/doctor/ai_diagnosis', methods=['GET', 'POST'])
def doctor_ai_diagnosis():
    if session.get('userType') != 'doctor':
        return redirect(url_for('login'))

    prediction = None

    if request.method == 'POST':
        if 'xray' not in request.files:
            flash('No file uploaded.')
            return redirect(request.url)

        file = request.files['xray']
        if file.filename == '':
            flash('No selected file.')
            return redirect(request.url)

        # Simulated result
        prediction = "AI Analysis: Possible Pneumonia Detected"

    return render_template(
        'doctor/doctor_ai_diagnosis.html',
        username=session.get('username'),
        prediction=prediction
    )

#modify doctor account details
@app.route('/doctor/account', methods=['GET', 'POST'])
def doctor_account():
    if session.get('userType') != 'doctor':
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctor WHERE USERID = %s", (user_id,))
    doctor = cursor.fetchone() 
    cursor.close()
    conn.close()

    return render_template('doctor/doctor_modifyaccount.html', doctor=doctor)


# Clinic Admin Home Page
@app.route('/admin_home')
def admin_home():
    if session.get('userType') == 'clinicadmin':
        return render_template('clinic_admin/adminhome.html', firstName=session.get('firstName'), lastName=session.get('lastName'))
    return redirect(url_for('login'))

@app.route('/admin_home/appointments')
def admin_appointmennts():
    if session.get('userType') != 'clinicadmin':
       return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    #Join appointments with patient info with of the corresponding clinic 
    cursor.execute("""
        SELECT a.apptID, a.appointment_date, a.appointment_time, a.symptoms, 
                   p.firstName, p.lastName

        FROM appointments a
        JOIN patient p ON a.patientID = p.USERID
        ORDER BY a.appointment_date, a.appointment_time 
    """)
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('/clinic_admin/AppointmentAdmin.html',
                           appointments=appointments,
                           username=session.get('username'))

@app.route('/admin_home/manage_accounts')
def admin_manageaccount():
    if session.get('userType') != 'clinicadmin':
         return redirect(url_for('login'))
    return render_template('/clinic_admin/ManageAccount.html',username=session.get('username'))

@app.route('/admin_home/manage_reports')
def admin_managereports():
    if session.get('userType') != 'clinicadmin':
        return render_template('/clinic_admin/ManageReports.html',username=session.get('username'))
    return redirect(url_for('login'))

@app.route('/admin_home/manage_appointments/book_appointment')
def admin_bookAppoimnent():
    if session.get('userType') != 'clinicadmin':
        return render_template('/clinic_admin/BookAppoiment.html',username=session.get('username'))
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))

# Search functionality for all users
@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    user_type = session.get('userType')
    user_id = session.get('user_id')
    clinic_id = session.get('clinicID')

    # Map month names to numbers
    month_map = {month.lower(): index for index, month in enumerate(calendar.month_name) if month}
    query_lower = query.lower()
    month_num = None
    year_num = None

    # Extract month and year from query
    for name, num in month_map.items():
        if name in query_lower:
            month_num = num
            # Try to extract a 4-digit year near the month name
            match = re.search(rf"{name}\s+(\d{{4}})", query_lower)
            if match:
                year_num = int(match.group(1))
            else:
                # Try the other way around: "2023 March"
                match = re.search(rf"(\d{{4}})\s+{name}", query_lower)
                if match:
                    year_num = int(match.group(1))
            break

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # --- APPOINTMENTS ---
    if user_type == 'patient':
        if month_num and year_num:
            cursor.execute("""
                SELECT a.apptID, a.patientID, a.appointment_date, a.appointment_time, a.doctorID, a.symptoms,
                       p.firstName, p.lastName
                FROM appointments a
                JOIN patient p ON a.patientID = p.USERID
                WHERE MONTH(a.appointment_date) = %s AND YEAR(a.appointment_date) = %s
                  AND a.patientID = %s
            """, (month_num, year_num, user_id))
        elif month_num:
            cursor.execute("""
                SELECT a.apptID, a.patientID, a.appointment_date, a.appointment_time, a.doctorID, a.symptoms,
                       p.firstName, p.lastName
                FROM appointments a
                JOIN patient p ON a.patientID = p.USERID
                WHERE MONTH(a.appointment_date) = %s
                  AND a.patientID = %s
            """, (month_num, user_id))
        else:
            cursor.execute("""
                SELECT a.apptID, a.patientID, a.appointment_date, a.appointment_time, a.doctorID, a.symptoms,
                       p.firstName, p.lastName
                FROM appointments a
                JOIN patient p ON a.patientID = p.USERID
                WHERE (a.symptoms LIKE %s OR a.appointment_date LIKE %s)
                  AND a.patientID = %s
            """, (f"%{query}%", f"%{query}%", user_id))
        appointments = cursor.fetchall()
    elif user_type == 'doctor':
        # Only appointments for this doctor
        if month_num and year_num:
            cursor.execute("""
                SELECT a.apptID, a.patientID, a.appointment_date, a.appointment_time, a.doctorID, a.symptoms,
                       p.firstName, p.lastName
                FROM appointments a
                JOIN patient p ON a.patientID = p.USERID
                WHERE MONTH(a.appointment_date) = %s AND YEAR(a.appointment_date) = %s
                  AND a.doctorID = %s
            """, (month_num, year_num, user_id))
        elif month_num:
            cursor.execute("""
                SELECT a.apptID, a.patientID, a.appointment_date, a.appointment_time, a.doctorID, a.symptoms,
                       p.firstName, p.lastName
                FROM appointments a
                JOIN patient p ON a.patientID = p.USERID
                WHERE MONTH(a.appointment_date) = %s
                  AND a.doctorID = %s
            """, (month_num, user_id))
        else:
            
            cursor.execute("""
                SELECT a.apptID, a.patientID, a.appointment_date, a.appointment_time, a.doctorID, a.symptoms,
                       p.firstName, p.lastName
                FROM appointments a
                JOIN patient p ON a.patientID = p.USERID
                WHERE (a.symptoms LIKE %s OR a.appointment_date LIKE %s OR p.firstName LIKE %s OR p.lastName LIKE %s)
                  AND a.doctorID = %s
            """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", user_id))
        appointments = cursor.fetchall()
    elif user_type == 'clinicadmin':
        # Only appointments for this clinic
        if month_num and year_num:
            cursor.execute("""
                SELECT a.apptID, a.patientID, a.appointment_date, a.appointment_time, a.doctorID, a.symptoms,
                       p.firstName, p.lastName
                FROM appointments a
                JOIN patient p ON a.patientID = p.USERID
                WHERE MONTH(a.appointment_date) = %s AND YEAR(a.appointment_date) = %s
                  AND a.clinicID = %s
            """, (month_num, year_num, clinic_id))
        elif month_num:
            cursor.execute("""
                SELECT a.apptID, a.patientID, a.appointment_date, a.appointment_time, a.doctorID, a.symptoms,
                       p.firstName, p.lastName
                FROM appointments a
                JOIN patient p ON a.patientID = p.USERID
                WHERE MONTH(a.appointment_date) = %s
                  AND a.clinicID = %s
            """, (month_num, clinic_id))
        else:
            cursor.execute("""
                SELECT a.apptID, a.patientID, a.appointment_date, a.appointment_time, a.doctorID, a.symptoms,
                       p.firstName, p.lastName
                FROM appointments a
                JOIN patient p ON a.patientID = p.USERID
                WHERE (a.symptoms LIKE %s OR a.appointment_date LIKE %s OR p.firstName LIKE %s OR p.lastName LIKE %s)
                  AND a.clinicID = %s
            """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", clinic_id))
        appointments = cursor.fetchall()
    else:
        # Default: show all
        if month_num and year_num:
            cursor.execute("""
                SELECT a.apptID, a.patientID, a.appointment_date, a.appointment_time, a.doctorID, a.symptoms,
                       p.firstName, p.lastName
                FROM appointments a
                JOIN patient p ON a.patientID = p.USERID
                WHERE MONTH(a.appointment_date) = %s AND YEAR(a.appointment_date) = %s
            """, (month_num, year_num))
        elif month_num:
            cursor.execute("""
                SELECT a.apptID, a.patientID, a.appointment_date, a.appointment_time, a.doctorID, a.symptoms,
                       p.firstName, p.lastName
                FROM appointments a
                JOIN patient p ON a.patientID = p.USERID
                WHERE MONTH(a.appointment_date) = %s
            """, (month_num,))
        else:
            
            cursor.execute("""
                SELECT a.apptID, a.patientID, a.appointment_date, a.appointment_time, a.doctorID, a.symptoms,
                       p.firstName, p.lastName
                FROM appointments a
                JOIN patient p ON a.patientID = p.USERID
                WHERE a.symptoms LIKE %s OR a.appointment_date LIKE %s OR p.firstName LIKE %s OR p.lastName LIKE %s
            """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
        appointments = cursor.fetchall()

    # --- REPORTS ---
    if user_type == 'patient':
        if month_num and year_num:
            cursor.execute("""
                SELECT r.reportID, r.patientID, r.doctorID, r.reportDate,
                       p.firstName AS patientFirstName, p.lastName AS patientLastName,
                       d.firstName AS doctorFirstName, d.lastName AS doctorLastName
                FROM Reports r
                JOIN patient p ON r.patientID = p.USERID
                JOIN doctor d ON r.doctorID = d.USERID
                WHERE MONTH(r.reportDate) = %s AND YEAR(r.reportDate) = %s AND r.patientID = %s
            """, (month_num, year_num, user_id))
        elif month_num:
            cursor.execute("""
                SELECT r.reportID, r.patientID, r.doctorID, r.reportDate,
                       p.firstName AS patientFirstName, p.lastName AS patientLastName,
                       d.firstName AS doctorFirstName, d.lastName AS doctorLastName
                FROM Reports r
                JOIN patient p ON r.patientID = p.USERID
                JOIN doctor d ON r.doctorID = d.USERID
                WHERE MONTH(r.reportDate) = %s AND r.patientID = %s
            """, (month_num, user_id))
        else:
            cursor.execute("""
                SELECT r.reportID, r.patientID, r.doctorID, r.reportDate,
                       p.firstName AS patientFirstName, p.lastName AS patientLastName,
                       d.firstName AS doctorFirstName, d.lastName AS doctorLastName
                FROM Reports r
                JOIN patient p ON r.patientID = p.USERID
                JOIN doctor d ON r.doctorID = d.USERID
                WHERE (
                    CAST(r.reportID AS CHAR) LIKE %s
                    OR CAST(r.patientID AS CHAR) LIKE %s
                    OR r.reportDate LIKE %s
                )
                AND r.patientID = %s
            """, (f"%{query}%", f"%{query}%", f"%{query}%", user_id))
        reports = cursor.fetchall()
    elif user_type == 'doctor':
        # Only reports for this doctor
        if month_num and year_num:
            cursor.execute("""
                SELECT r.reportID, r.patientID, r.doctorID, r.reportDate,
                       p.firstName AS patientFirstName, p.lastName AS patientLastName,
                       d.firstName AS doctorFirstName, d.lastName AS doctorLastName
                FROM Reports r
                JOIN patient p ON r.patientID = p.USERID
                JOIN doctor d ON r.doctorID = d.USERID
                WHERE MONTH(r.reportDate) = %s AND YEAR(r.reportDate) = %s AND r.doctorID = %s
            """, (month_num, year_num, user_id))
        elif month_num:
            cursor.execute("""
                SELECT r.reportID, r.patientID, r.doctorID, r.reportDate,
                       p.firstName AS patientFirstName, p.lastName AS patientLastName,
                       d.firstName AS doctorFirstName, d.lastName AS doctorLastName
                FROM Reports r
                JOIN patient p ON r.patientID = p.USERID
                JOIN doctor d ON r.doctorID = d.USERID
                WHERE MONTH(r.reportDate) = %s AND r.doctorID = %s
            """, (month_num, user_id))
        else:
          
            cursor.execute("""
                SELECT r.reportID, r.patientID, r.doctorID, r.reportDate,
                       p.firstName AS patientFirstName, p.lastName AS patientLastName,
                       d.firstName AS doctorFirstName, d.lastName AS doctorLastName
                FROM Reports r
                JOIN patient p ON r.patientID = p.USERID
                JOIN doctor d ON r.doctorID = d.USERID
                WHERE (
                    CAST(r.reportID AS CHAR) LIKE %s
                    OR CAST(r.patientID AS CHAR) LIKE %s
                    OR r.reportDate LIKE %s
                    OR p.firstName LIKE %s
                    OR p.lastName LIKE %s
                )
                AND r.doctorID = %s
            """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", user_id))
        reports = cursor.fetchall()
    elif user_type == 'clinicadmin':
        # Only reports for this clinic 
        if month_num and year_num:
            cursor.execute("""
                SELECT r.reportID, r.patientID, r.doctorID, r.reportDate,
                       p.firstName AS patientFirstName, p.lastName AS patientLastName,
                       d.firstName AS doctorFirstName, d.lastName AS doctorLastName
                FROM Reports r
                JOIN patient p ON r.patientID = p.USERID
                JOIN doctor d ON r.doctorID = d.USERID
                WHERE MONTH(r.reportDate) = %s AND YEAR(r.reportDate) = %s AND p.clinicID = %s
            """, (month_num, year_num, clinic_id))
        elif month_num:
            cursor.execute("""
                SELECT r.reportID, r.patientID, r.doctorID, r.reportDate,
                       p.firstName AS patientFirstName, p.lastName AS patientLastName,
                       d.firstName AS doctorFirstName, d.lastName AS doctorLastName
                FROM Reports r
                JOIN patient p ON r.patientID = p.USERID
                JOIN doctor d ON r.doctorID = d.USERID
                WHERE MONTH(r.reportDate) = %s AND p.clinicID = %s
            """, (month_num, clinic_id))
        else:
        
            cursor.execute("""
                SELECT r.reportID, r.patientID, r.doctorID, r.reportDate,
                       p.firstName AS patientFirstName, p.lastName AS patientLastName,
                       d.firstName AS doctorFirstName, d.lastName AS doctorLastName
                FROM Reports r
                JOIN patient p ON r.patientID = p.USERID
                JOIN doctor d ON r.doctorID = d.USERID
                WHERE (
                    CAST(r.reportID AS CHAR) LIKE %s
                    OR CAST(r.patientID AS CHAR) LIKE %s
                    OR r.reportDate LIKE %s
                    OR p.firstName LIKE %s
                    OR p.lastName LIKE %s
                )
                AND p.clinicID = %s
            """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", clinic_id))
        reports = cursor.fetchall()
    else:
        # Default: show all
        if month_num and year_num:
            cursor.execute("""
                SELECT r.reportID, r.patientID, r.doctorID, r.reportDate,
                       p.firstName AS patientFirstName, p.lastName AS patientLastName,
                       d.firstName AS doctorFirstName, d.lastName AS doctorLastName
                FROM Reports r
                JOIN patient p ON r.patientID = p.USERID
                JOIN doctor d ON r.doctorID = d.USERID
                WHERE MONTH(r.reportDate) = %s AND YEAR(r.reportDate) = %s
            """, (month_num, year_num))
        elif month_num:
            cursor.execute("""
                SELECT r.reportID, r.patientID, r.doctorID, r.reportDate,
                       p.firstName AS patientFirstName, p.lastName AS patientLastName,
                       d.firstName AS doctorFirstName, d.lastName AS doctorLastName
                FROM Reports r
                JOIN patient p ON r.patientID = p.USERID
                JOIN doctor d ON r.doctorID = d.USERID
                WHERE MONTH(r.reportDate) = %s
            """, (month_num,))
        else:
            # Add patient name search for default
            cursor.execute("""
                SELECT r.reportID, r.patientID, r.doctorID, r.reportDate,
                       p.firstName AS patientFirstName, p.lastName AS patientLastName,
                       d.firstName AS doctorFirstName, d.lastName AS doctorLastName
                FROM Reports r
                JOIN patient p ON r.patientID = p.USERID
                JOIN doctor d ON r.doctorID = d.USERID
                WHERE
                    CAST(r.reportID AS CHAR) LIKE %s
                    OR CAST(r.patientID AS CHAR) LIKE %s
                    OR r.reportDate LIKE %s
                    OR p.firstName LIKE %s
                    OR p.lastName LIKE %s
            """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
        reports = cursor.fetchall()

    # --- PATIENTS (for doctor and clinicadmin) ---
    patients = []
    if user_type == 'doctor':
        cursor.execute("""
            SELECT USERID, firstName, lastName, email, phone, dateofbirth
            FROM patient
            WHERE firstName LIKE %s OR lastName LIKE %s OR email LIKE %s OR phone LIKE %s
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
        patients = cursor.fetchall()
    elif user_type == 'clinicadmin':
        cursor.execute("""
            SELECT USERID, firstName, lastName, email, phone, dateofbirth
            FROM patient
            WHERE clinicID = %s AND (
                firstName LIKE %s OR lastName LIKE %s OR email LIKE %s OR phone LIKE %s
            )
        """, (clinic_id, f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
        patients = cursor.fetchall()

    cursor.close()
    conn.close()

    results = {
        "appointments": appointments,
        "reports": reports,
        "patients": patients
    }

    # Pass userType and user info for dynamic navbar
    user_type = session.get('userType')
    username = session.get('username')
    first_name = session.get('firstName')
    last_name = session.get('lastName')
    return render_template(
        "search_results.html",
        query=query,
        results=results,
        user_type=user_type,
        username=username,
        first_name=first_name,
        last_name=last_name
    )

# Appointment route for linking search results to appointment page with ability to show details
@app.route('/patient/appointments/detail')
def p_appointments_search():
    apptID = request.args.get('apptID')
    if not apptID or session.get('userType') != 'patient':
        return redirect(url_for('login'))
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM appointments WHERE apptID = %s", (apptID,))
    appointment = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('patient/p_appointments.html', appointment=appointment)

# Appointment route for doctor to view appointment details on appointment page
@app.route('/doctor/appointments/detail')
def doctor_appointments_search():
    apptID = request.args.get('apptID')
    if not apptID or session.get('userType') != 'doctor':
        return redirect(url_for('login'))
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM appointments WHERE apptID = %s", (apptID,))
    appointment = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('doctor/doctor_appointments.html', appointment=appointment)

# Appointment route for clinic admin to view appointment details on appointment page
@app.route('/admin/appointments/detail')
def admin_appointments_search():
    apptID = request.args.get('apptID')
    if not apptID or session.get('userType') != 'clinicadmin':
        return redirect(url_for('login'))
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM appointments WHERE apptID = %s", (apptID,))
    appointment = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('clinic_admin/AppointmentAdmin.html', appointment=appointment)

# Report route for patient to view report details on reports page
@app.route('/patient/reports/detail')
def patient_reports_search():
    reportID = request.args.get('reportID')
    if not reportID or session.get('userType') != 'patient':
        return redirect(url_for('login'))
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Reports WHERE reportID = %s", (reportID,))
    report = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('patient/reportdetails.html', report=report)

# Report route for doctor to view report details on reports page
@app.route('/doctor/reports/detail')
def doctor_reports_search():
    reportID = request.args.get('reportID')
    if not reportID or session.get('userType') != 'doctor':
        return redirect(url_for('login'))
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Reports WHERE reportID = %s", (reportID,))
    report = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('doctor/doctor_reports.html', report=report)

# Report route for clinic admin to view report details on reports page
@app.route('/admin/reports/detail')
def admin_reports_search():
    reportID = request.args.get('reportID')
    if not reportID or session.get('userType') != 'clinicadmin':
        return redirect(url_for('login'))
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Reports WHERE reportID = %s", (reportID,))
    report = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('clinic_admin/ManageReports.html', report=report)

if __name__ == '__main__':
    app.run(debug=True)