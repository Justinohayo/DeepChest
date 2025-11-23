from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import webbrowser
import calendar
import re
from datetime import date, datetime
import json

app = Flask(__name__)
app.secret_key = '1234'  # Needed for flash messages and sessions

# Database connection config
db_config = {
    'host': 'mysql-database.cjogeuu2gnn5.ca-central-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'AdminIPA',
    'database': 'DeepChest_DB'
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
        SELECT a.apptID, a.appointment_date, a.appointment_time, d.firstName AS doctorFirstName, d.lastName AS doctorLastName, a.symptoms
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

# Handle the selection of an appointment to edit
@app.route('/patient/edit-appointments', methods=['POST'])
def patient_edit_appointments():
    if session.get('userType') != 'patient':
        return redirect(url_for('login'))
    appointment_id = request.form.get('appointment_id')
    if not appointment_id:
        flash('Please select an appointment to edit.')
        return redirect(url_for('patient_appointments'))
    try:
        appointment_id = int(appointment_id)
    except ValueError:
        flash('Invalid appointment selected.')
        return redirect(url_for('patient_appointments'))
    return redirect(url_for('patient_manage_appointment', appointment_id=appointment_id))

# Show the manage/edit appointment page
@app.route('/patient/manage-appointment/<int:appointment_id>', methods=['GET', 'POST'])
def patient_manage_appointment(appointment_id):
    if session.get('userType') != 'patient':
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    # Fetch the appointment for this patient
    cursor.execute("""
        SELECT a.apptID, a.appointment_date, a.appointment_time, a.symptoms,
               a.doctorID AS doctorID,
               d.firstName AS doctorFirstName, d.lastName AS doctorLastName
        FROM appointments a
        JOIN doctor d ON a.doctorID = d.USERID
        WHERE a.apptID = %s AND a.patientID = %s
    """, (appointment_id, user_id))
    appointment = cursor.fetchone()

    if not appointment:
        cursor.close()
        conn.close()
        flash("Appointment not found.", "danger")
        return redirect(url_for('patient_appointments'))

    if request.method == 'POST':
        # Update date/time/symptoms. Validate conflicts for the assigned doctor.
        new_symptoms = request.form.get('symptoms')
        new_date = request.form.get('appointment_date')
        new_time = request.form.get('appointment_time')

        # Normalize time format if needed (allow HH:MM)
        if new_time and len(new_time) == 5:
            new_time = new_time + ':00'

        # If doctorID exists, check for conflicts excluding this appointment
        doctor_id = None
        try:
            # appointment may be dict-like
            doctor_id = appointment.get('doctorID') if isinstance(appointment, dict) else appointment[ 'doctorID' ] if appointment else None
        except Exception:
            doctor_id = None

        if doctor_id and new_date and new_time:
            cursor.execute("SELECT apptID FROM appointments WHERE doctorID = %s AND appointment_date = %s AND appointment_time = %s AND apptID != %s", (doctor_id, new_date, new_time, appointment_id))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                flash('Selected time slot is not available for your doctor. Please choose another time.')
                return redirect(url_for('patient_manage_appointment', appointment_id=appointment_id))

        # Perform update (only fields provided)
        try:
            cursor.execute("""
                UPDATE appointments SET appointment_date = %s, appointment_time = %s, symptoms = %s
                WHERE apptID = %s AND patientID = %s
            """, (new_date, new_time, new_symptoms, appointment_id, user_id))
            conn.commit()
            flash('Appointment updated successfully!')
            cursor.close()
            conn.close()
            return redirect(url_for('patient_appointments'))
        except mysql.connector.Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash('Database error: ' + str(e))
            return redirect(url_for('patient_manage_appointment', appointment_id=appointment_id))

    cursor.close()
    conn.close()

    # Normalize appointment fields so they are JSON-serializable for the template
    appt_for_template = {}
    if isinstance(appointment, dict):
        for k, v in appointment.items():
            # Dates -> YYYY-MM-DD
            if k in ('appointment_date', 'reportDate') and hasattr(v, 'strftime'):
                try:
                    appt_for_template[k] = v.strftime('%Y-%m-%d')
                except Exception:
                    appt_for_template[k] = str(v)
            # Times: could be time or timedelta depending on driver
            elif k == 'appointment_time':
                if v is None:
                    appt_for_template[k] = None
                else:
                    # datetime.time
                    if hasattr(v, 'strftime'):
                        appt_for_template[k] = v.strftime('%H:%M:%S')
                    # timedelta (mysql sometimes returns TIME as timedelta)
                    elif hasattr(v, 'total_seconds'):
                        secs = int(v.total_seconds())
                        hh = secs // 3600
                        mm = (secs % 3600) // 60
                        ss = secs % 60
                        appt_for_template[k] = f"{hh:02d}:{mm:02d}:{ss:02d}"
                    else:
                        appt_for_template[k] = str(v)
            else:
                appt_for_template[k] = v
    else:
        # Fallback: just pass the original object (template will likely fail if not serializable)
        appt_for_template = appointment

    return render_template('patient/p_manageappointments.html', appointment=appt_for_template)

@app.route('/patient/book-appointment', methods=['GET', 'POST'])
def patient_book_appointment():
    if session.get('userType') != 'patient':
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    if request.method == 'POST':
        # Collect form inputs
        appointment_date = request.form.get('appointment_date')  # expected YYYY-MM-DD
        appointment_time = request.form.get('appointment_time')  # expected HH:MM:SS
        symptoms = request.form.get('symptoms')

        if not appointment_date or not appointment_time:
            flash('Please select a date and time for your appointment.')
            return redirect(url_for('patient_book_appointment'))

        # Normalize time (allow HH:MM or HH:MM:SS)
        if len(appointment_time) == 5:
            appointment_time = appointment_time + ':00'

        # Fetch patient's doctor and clinic
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT doctorID, clinicID FROM patient WHERE USERID = %s", (user_id,))
        prow = cursor.fetchone()
        doctor_id = None
        clinic_id = None
        if prow:
            try:
                doctor_id = prow[0]
                clinic_id = prow[1]
            except Exception:
                # handle dict cursor vs tuple
                doctor_id = prow.get('doctorID') if isinstance(prow, dict) else None
                clinic_id = prow.get('clinicID') if isinstance(prow, dict) else None

        # If no doctor assigned, we still allow booking without doctor (doctorID NULL)

        # Check for conflict (same doctor, same date/time)
        if doctor_id:
            cursor.execute("SELECT apptID FROM appointments WHERE doctorID = %s AND appointment_date = %s AND appointment_time = %s", (doctor_id, appointment_date, appointment_time))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                flash('Selected time slot is not available. Please choose another time.')
                return redirect(url_for('patient_book_appointment'))

        # Insert appointment
        try:
            cursor.execute("INSERT INTO appointments (patientID, appointment_date, appointment_time, doctorID, clinicID, symptoms) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, appointment_date, appointment_time, doctor_id, clinic_id, symptoms))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Appointment booked successfully!')
            return redirect(url_for('patient_appointments'))
        except mysql.connector.Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash('Database error: ' + str(e))
            return redirect(url_for('patient_book_appointment'))

    # GET: render calendar with patient's existing appointment dates
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT appointment_date FROM appointments WHERE patientID = %s", (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    existing_dates = []
    for r in rows:
        try:
            d = r[0]
        except Exception:
            d = r.get('appointment_date') if isinstance(r, dict) else None
        if d:
            # format to YYYY-MM-DD
            if hasattr(d, 'strftime'):
                existing_dates.append(d.strftime('%Y-%m-%d'))
            else:
                existing_dates.append(str(d))

    return render_template('patient/p_bookappointment.html', existing_appointments=existing_dates)


@app.route('/patient/booked_times')
def patient_booked_times():
    # Returns JSON list of times already booked for the patient's doctor on a date
    if session.get('userType') != 'patient':
        return json.dumps([]), 401
    user_id = session.get('user_id')
    date_q = request.args.get('date')
    if not date_q:
        return json.dumps([]), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # get doctor for this patient
    cursor.execute("SELECT doctorID FROM patient WHERE USERID = %s", (user_id,))
    prow = cursor.fetchone()
    doctor_id = None
    if prow:
        try:
            doctor_id = prow[0]
        except Exception:
            doctor_id = prow.get('doctorID') if isinstance(prow, dict) else None
    if not doctor_id:
        cursor.close()
        conn.close()
        return json.dumps([])
    cursor.execute("SELECT appointment_time FROM appointments WHERE doctorID = %s AND appointment_date = %s", (doctor_id, date_q))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    times = [r[0].strftime('%H:%M:%S') if hasattr(r[0], 'strftime') else str(r[0]) for r in rows]
    return json.dumps(times)

# Patient Reports Page
#@app.route('/patient/reports')
#def patient_reports():
    #if session.get('userType') == 'patient':
       # user_id = session.get('user_id')
        #conn = mysql.connector.connect(**db_config)
        #cursor = conn.cursor(dictionary=True)
        #cursor.execute("""
           # SELECT r.reportID,r.files, r.reportDate, r.doctorID,
             #      d.firstName AS doctorFirstName, d.lastName AS doctorLastName
            #FROM Reports r
           # JOIN doctor d ON r.doctorID = d.USERID
           # WHERE r.patientID = %s
           # ORDER BY r.reportDate DESC
       # """, (user_id,))
        #reports = cursor.fetchall()
       # cursor.close()
       # conn.close()
       # for r in reports:
           # if isinstance(r['reportDate'], str):
               # try:
                    #r['reportDate'] = datetime.strptime(r['reportDate'], '%Y-%m-%d')
               # except Exception:
                   # pass
       # return render_template(
            #'patient/myreports.html',
           # user_id=user_id,
           # reports=reports
        #)
    #return redirect(url_for('login'))

#@app.route('/patient/search_reports', methods=['GET'])
#def search_reports():
    #if session.get('userType') != 'patient':
        #return redirect(url_for('login'))
    #user_id = session.get('user_id')
   # query = request.args.get('query', '').strip()

    # Month name support
   # month_map = {month.lower(): index for index, month in enumerate(calendar.month_name) if month}
    #query_lower = query.lower()
    #month_num = None
    #year_num = None
    #for name, num in month_map.items():
       # if name in query_lower:
           # month_num = num
           # match = re.search(rf"{name}\s+(\d{{4}})", query_lower)
            #if match:
                #year_num = int(match.group(1))
            #else:
                #match = re.search(rf"(\d{{4}})\s+{name}", query_lower)
                #if match:
                   # year_num = int(match.group(1))
           # break

   # conn = mysql.connector.connect(**db_config)
   # cursor = conn.cursor(dictionary=True)
   # if month_num and year_num:
        #cursor.execute("""
            #SELECT r.reportID,r.files, r.reportDate, r.doctorID,
                  # d.firstName AS doctorFirstName, d.lastName AS doctorLastName
            #FROM Reports r
            #JOIN doctor d ON r.doctorID = d.USERID
            #WHERE r.patientID = %s AND MONTH(r.reportDate) = %s AND YEAR(r.reportDate) = %s
           # ORDER BY r.reportDate DESC
       # """, (user_id, month_num, year_num))
    #elif month_num:
        #cursor.execute("""
           # SELECT r.reportID,r.files, r.reportDate, r.doctorID,
                  # d.firstName AS doctorFirstName, d.lastName AS doctorLastName
            #FROM Reports r
            #JOIN doctor d ON r.doctorID = d.USERID
            #WHERE r.patientID = %s AND MONTH(r.reportDate) = %s
            #ORDER BY r.reportDate DESC
        #""", (user_id, month_num))
   # else:
        #cursor.execute("""
           # SELECT r.reportID,r.files, r.reportDate, r.doctorID,
              #     d.firstName AS doctorFirstName, d.lastName AS doctorLastName
           # FROM Reports r
            #JOIN doctor d ON r.doctorID = d.USERID
            #WHERE r.patientID = %s AND (
            #    CAST(r.reportID AS CHAR) LIKE %s
            #    OR r.reportDate LIKE %s
            #    OR d.firstName LIKE %s
            #    OR d.lastName LIKE %s
            #)
            #ORDER BY r.reportDate DESC
       # """, (user_id, f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
   # reports = cursor.fetchall()
    #cursor.close()
   # conn.close()
   # return render_template(
        #'patient/myreports.html',
       # user_id=user_id,
       # reports=reports
   # )

# Report details page for patients
#@app.route('/patient/report_details')
#def patient_report_details():
   # if session.get('userType') != 'patient':
      #  return redirect(url_for('login'))
   # report_id = request.args.get('reportID')
   # user_id = session.get('user_id')
   # conn = mysql.connector.connect(**db_config)
   # cursor = conn.cursor(dictionary=True)
   # cursor.execute("""
     #   SELECT r.*, d.firstName AS doctorFirstName, d.lastName AS doctorLastName
    #    FROM Reports r
    #    JOIN doctor d ON r.doctorID = d.USERID
   # WHERE r.reportID = %s AND r.patientID = %s
   # """, (report_id, user_id))
   # report = cursor.fetchone()
   # cursor.close()
   # conn.close()
  #  if not report:
        #flash("Report not found.", "danger")
      #  return redirect(url_for('patient_reports'))
   # return render_template('patient/reportdetails.html', report=report)

# Patient Messages Page (GET: show form, POST: send/save message)
@app.route('/patient/messages', methods=['GET', 'POST'])
def patient_messages():
    if session.get('userType') != 'patient':
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    # Get DB connection and fetch doctors for the select box
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        clinic_id = session.get('clinicID')
        if clinic_id:
            cursor.execute('SELECT USERID, firstName, lastName FROM doctor WHERE clinicID = %s', (clinic_id,))
        else:
            cursor.execute('SELECT USERID, firstName, lastName FROM doctor')
        doctors = cursor.fetchall()

        if request.method == 'POST':
            doctor_id = request.form.get('doctorID')
            subject = (request.form.get('subject') or '').strip()
            body = (request.form.get('body') or '').strip()

            # Basic validation
            if not doctor_id:
                flash('Please select a doctor to send the message to.', 'error')
                return render_template('patient/messages.html', doctors=doctors)
            if not subject:
                flash('Please provide a subject for the message.', 'error')
                return render_template('patient/messages.html', doctors=doctors)
            if not body:
                flash('Please write a message.', 'error')
                return render_template('patient/messages.html', doctors=doctors)

            try:
                ins = conn.cursor()
                # messages table schema: (messageID, patientID, doctorID, content, time_sent)
                # There is no separate subject column; store subject+body together in content
                content = f"Subject: {subject}\n\n{body}"
                ins.execute(
                    'INSERT INTO messages (patientID, doctorID, content) VALUES (%s, %s, %s)',
                    (user_id, doctor_id, content)
                )
                conn.commit()
                flash('Message sent successfully.', 'success')
                ins.close()
                cursor.close()
                conn.close()
                return redirect(url_for('patient_messages'))
            except mysql.connector.Error as e:
                conn.rollback()
                flash('Failed to send message: {}'.format(str(e)), 'error')
                return render_template('patient/messages.html', doctors=doctors)

        # GET
        cursor.close()
        conn.close()
        return render_template('patient/messages.html', doctors=doctors)

    except mysql.connector.Error as err:
        flash('Database error: {}'.format(err), 'error')
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
        return render_template('patient/messages.html', doctors=[])

# Patient Notifications Page (GET: show form, POST: opt-in)
@app.route('/patient/notifications', methods=['GET', 'POST'])
def patient_notifications():
    if session.get('userType') != 'patient':
        return redirect(url_for('login'))
    user_id = session.get('user_id')

    if request.method == 'POST':
        method = (request.form.get('method') or '').strip().lower()
        contact = (request.form.get('contact') or '').strip()

        if method not in ('phone', 'email') or not contact:
            flash('Please select a valid notification method and provide contact details.', 'error')
            return render_template('patient/notifications.html', user_id=user_id)

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            # Add data into notifications table
            cursor.execute(
                """
                INSERT INTO notifications (patientID, notification_type, contact_info, notification_status)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  notification_type = VALUES(notification_type),
                  contact_info = VALUES(contact_info),
                  notification_status = VALUES(notification_status)
                """,
                (user_id, method, contact, 1)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('You have successfully opted in for notifications.', 'success')
            return redirect(url_for('patient_notifications'))
        except mysql.connector.Error as e:
            try:
                conn.rollback()
            except Exception:
                pass
            flash('Database error: {}'.format(str(e)), 'error')
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass
            return render_template('patient/notifications.html', user_id=user_id)

    # GET
    return render_template('patient/notifications.html', user_id=user_id)


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

# Add Child Page for Patient (GET shows form, POST creates child)
@app.route('/patient/add-child', methods=['GET', 'POST'])
def add_child():
    if session.get('userType') != 'patient':
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    if request.method == 'POST':
        # Handle child creation (merged POST logic)
        parent_id = session.get('user_id')

        # Collect form data
        clinicID = request.form.get('clinicID') or request.form.get('clinic') or session.get('clinicID')
        doctorID = request.form.get('doctorID') or session.get('doctorID') or None
        firstName = request.form.get('firstName', '').strip()
        lastName = request.form.get('lastName', '').strip()
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip() or email
        phoneNumber = request.form.get('phoneNumber', '').strip()
        password = request.form.get('password', '').strip()
        birthday = request.form.get('birthday', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        province = request.form.get('province', '').strip()
        postalCode = request.form.get('postalCode', '').strip()
        insurance = request.form.get('insurance', '').strip()

        # Basic validation
        if not firstName or not lastName or not password:
            flash('Please provide at minimum first name, last name and password for the child.')
            return redirect(url_for('add_child'))

        # Compute age when birthday provided
        age = None
        if birthday:
            try:
                dob = datetime.strptime(birthday, '%Y-%m-%d').date()
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            except Exception:
                dob = None
                age = None
        else:
            dob = None

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Ensure parent has an email on file
        cursor.execute("SELECT email FROM patient WHERE USERID = %s", (parent_id,))
        parent_row = cursor.fetchone()
        parent_email = None
        if parent_row:
            try:
                parent_email = parent_row[0]
            except Exception:
                parent_email = parent_row.get('email') if isinstance(parent_row, dict) else None

        if not parent_email and not session.get('email'):
            cursor.close()
            conn.close()
            flash('Please add your email to your account before registering a child.')
            return redirect(url_for('patient_account'))

        try:
            # Check if email already exists in patient table
            if email:
                cursor.execute("SELECT USERID FROM patient WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Email is already in use. Choose a different email.')
                    cursor.close()
                    conn.close()
                    return redirect(url_for('add_child'))

            # Insert into login table for the child
            cursor.execute(
                "INSERT INTO login (username, password, userType, clinicID) VALUES (%s, %s, %s, %s)",
                (username, password, 'patient', clinicID)
            )
            child_userid = cursor.lastrowid

            # Insert into patient table for the child
            cursor.execute(
                "INSERT INTO patient (firstName, lastName, age, dateofbirth, USERID, address, city, province, postalCode, phone, email, insurance, doctorID, childID, clinicID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (firstName, lastName, age, dob, child_userid, address, city, province, postalCode, phoneNumber, email, insurance, doctorID or None, None, clinicID)
            )

            # Create a childLink row linking to the parent
            cursor.execute("INSERT INTO childLink (parentID) VALUES (%s)", (parent_id,))
            link_id = cursor.lastrowid

            # Create a child row referencing the link and parent
            cursor.execute("INSERT INTO child (linkID, parentID) VALUES (%s, %s)", (link_id, parent_id))
            child_id = cursor.lastrowid

            # Update the child's patient row to store the childID (if desired by schema)
            cursor.execute("UPDATE patient SET childID = %s WHERE USERID = %s", (str(child_id), child_userid))

            conn.commit()
            flash('Child account created successfully!')
            cursor.close()
            conn.close()
            return redirect(url_for('patient_home'))
        except mysql.connector.Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash('Database error: ' + str(e))
            return redirect(url_for('add_child'))

    # GET: show form
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Fetch patient info
    cursor.execute("SELECT * FROM patient WHERE USERID = %s", (user_id,))
    patient = cursor.fetchone()

    # Determine clinicID and doctorID (prefer patient table values)
    clinic_id = None
    doctor_id = None
    if patient:
        clinic_id = patient.get('clinicID')
        doctor_id = patient.get('doctorID')

    # Fallback to session values if DB values missing
    if not clinic_id:
        clinic_id = session.get('clinicID')
    if not doctor_id:
        doctor_id = session.get('doctorID')

    # Fetch clinic info
    clinic = None
    if clinic_id:
        cursor.execute("SELECT * FROM clinic WHERE clinicID = %s", (clinic_id,))
        clinic = cursor.fetchone()

    # Fetch doctor info
    doctor = None
    if doctor_id:
        cursor.execute("SELECT * FROM doctor WHERE USERID = %s", (doctor_id,))
        doctor = cursor.fetchone()

    cursor.close()
    conn.close()

    # Render template with DB-provided objects (may be None)
    return render_template('patient/add-child.html', patient=patient, doctor=doctor, clinic=clinic)




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


@app.route('/doctor/search_appointments', methods=['GET'])
def search_appointments():
    if session.get('userType') != 'doctor':
        return redirect(url_for('login'))

    # Get search text from the input field
    search_term = request.args.get('query', '').strip()

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if search_term:
        cursor.execute("""
            SELECT a.apptID, a.appointment_date, a.appointment_time, a.symptoms,
                   p.firstName, p.lastName
            FROM appointments a
            JOIN patient p ON a.patientID = p.USERID
            WHERE p.firstName LIKE %s
               OR p.lastName LIKE %s
               OR a.symptoms LIKE %s
               OR a.appointment_date LIKE %s
            ORDER BY a.appointment_date, a.appointment_time
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
    else:
        # If no search term, show all appointments
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
                           username=session.get('username'),
                           query=search_term)



# Database connection helper
def get_db_connection():
    """Create and return a new MySQL database connection."""
    return mysql.connector.connect(**db_config)


# Doctor Patients Page
@app.route('/doctor/patients')
def doctor_patients():
    if session.get('userType') != 'doctor':
        return redirect(url_for('login'))

    doctor_id = session.get('user_id')
    doctor_username = session.get('username')

    if not doctor_id:
        return "Doctor not found", 404

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.firstName, p.lastName, p.age, p.dateofbirth, p.phone, p.email,
               p.address, p.city, p.province, p.postalCode, p.insurance
        FROM patient p
        WHERE p.doctorID = %s
    """, (doctor_id,))

    patients = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('doctor/doctor_patients.html',
                           username=doctor_username,
                           patients=patients)


# Doctor Search Patients Route
@app.route('/doctor/search_patients', methods=['GET'])
def doctor_search_patients():
    if session.get('userType') != 'doctor':
        return redirect(url_for('login'))

    doctor_id = session.get('user_id')
    doctor_username = session.get('username')

    if not doctor_id:
        return "Doctor not found", 404

    # Get search query and normalize
    query = request.args.get('query', '').strip()
    search_query = f"%{query.lower()}%"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if query:
        # Case-insensitive search with trimmed fields
        cursor.execute("""
            SELECT p.firstName, p.lastName, p.age, p.dateofbirth, p.phone, p.email,
                   p.address, p.city, p.province, p.postalCode, p.insurance
            FROM patient p
            WHERE p.doctorID = %s AND (
                LOWER(TRIM(p.firstName)) LIKE %s OR
                LOWER(TRIM(p.lastName)) LIKE %s OR
                LOWER(TRIM(p.email)) LIKE %s OR
                LOWER(TRIM(p.phone)) LIKE %s OR
                LOWER(TRIM(p.city)) LIKE %s
            )
            ORDER BY p.lastName, p.firstName
        """, (doctor_id, search_query, search_query, search_query, search_query, search_query))
    else:
        # If no query, return all patients for this doctor
        cursor.execute("""
            SELECT p.firstName, p.lastName, p.age, p.dateofbirth, p.phone, p.email,
                   p.address, p.city, p.province, p.postalCode, p.insurance
            FROM patient p
            WHERE p.doctorID = %s
            ORDER BY p.lastName, p.firstName
        """, (doctor_id,))

    patients = cursor.fetchall()
    cursor.close()
    conn.close()

    # Render template with results and original query
    return render_template(
        'doctor/doctor_patients.html',
        username=doctor_username,
        patients=patients,
        query=query
    )



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
        SELECT r.reportID, r.files, p.firstName, p.lastName, r.reportDate
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


@app.route('/doctor/search_reports', methods=['GET'])
def doctor_search_reports():
    if session.get('userType') != 'doctor':
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

    # If user typed "March 2024" or similar
    if month_num and year_num:
        cursor.execute("""
            SELECT r.reportID, r.reportDate, r.files,
                   p.firstName AS patientFirstName, p.lastName AS patientLastName
            FROM Reports r
            JOIN patient p ON r.patientID = p.USERID
            WHERE r.doctorID = %s AND MONTH(r.reportDate) = %s AND YEAR(r.reportDate) = %s
            ORDER BY r.reportDate DESC
        """, (user_id, month_num, year_num))

    # If user typed just "March"
    elif month_num:
        cursor.execute("""
            SELECT r.reportID, r.reportDate, r.files,
                   p.firstName AS patientFirstName, p.lastName AS patientLastName
            FROM Reports r
            JOIN patient p ON r.patientID = p.USERID
            WHERE r.doctorID = %s AND MONTH(r.reportDate) = %s
            ORDER BY r.reportDate DESC
        """, (user_id, month_num))

    # Generic keyword search (report ID, date, patient name)
    else:
        cursor.execute("""
            SELECT r.reportID, r.reportDate, r.files,
                   p.firstName AS patientFirstName, p.lastName AS patientLastName
            FROM Reports r
            JOIN patient p ON r.patientID = p.USERID
            WHERE r.doctorID = %s AND (
                CAST(r.reportID AS CHAR) LIKE %s
                OR r.reportDate LIKE %s
                OR p.firstName LIKE %s
                OR p.lastName LIKE %s
            )
            ORDER BY r.reportDate DESC
        """, (user_id, f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))

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

#request to modify doctor account details
@app.route('/doctor/account', methods=['GET', 'POST'])
def doctor_account():
    if session.get('userType') != 'doctor':
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Always fetch current info to display
    cursor.execute("SELECT * FROM doctor WHERE USERID = %s", (user_id,))
    doctor = cursor.fetchone()

    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        phone = request.form.get('phoneNumber')

        # Instead of updating the doctor table, insert a request
        cursor.execute("""
            INSERT INTO account_update_requests (
                doctorID, requested_firstName, requested_lastName, 
                requested_email, requested_phone
            ) VALUES (%s, %s, %s, %s, %s)
        """, (user_id, first_name, last_name, email, phone))
        conn.commit()

        cursor.close()
        conn.close()

        flash("Your update request has been sent to the admin for approval.", "info")
        return render_template('doctor/doctor_modifyaccount.html', doctor=doctor)

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