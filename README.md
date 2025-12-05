# DeepChest - AI-Powered Chest X-Ray Diagnostic System

DeepChest is a comprehensive Flask-based web application that provides AI-assisted chest X-ray diagnosis using deep learning and Grad-CAM visualization. The system supports multiple user types (patients, doctors, and clinic administrators) with features for appointment management, medical report generation, and diagnostic imaging analysis.

## Features

### AI-Powered Diagnosis
- **Deep Learning Model**: Uses a trained Keras model (`model_1.keras`) to classify chest X-rays into four categories:
  - COVID-19
  - Normal
  - Pneumonia
  - Tuberculosis
- **Grad-CAM Visualization**: Generates gradient-weighted class activation maps to highlight regions of interest in X-ray images
- **Confidence Scoring**: Provides probability scores for all diagnostic categories

### User Roles

#### Patients
- Book and manage appointments
- View medical reports and X-ray results
- Manage personal account information
- Opt-in to email notifications
- Add child accounts
- Search through appointments and reports

#### Doctors
- View and manage patient appointments
- Access AI-assisted diagnosis tools
- Generate comprehensive PDF medical reports with AI predictions
- View patient lists and medical histories
- Search appointments, patients, and reports

#### Clinic Administrators
- Manage clinic information and settings
- Oversee all clinic appointments
- Book appointments for patients
- Manage user accounts (patients and doctors)
- View and manage clinic reports
- Filter reports by date or expiry

### Report Generation
- Automated PDF generation with patient information
- AI diagnosis integration with confidence scores
- Clinic branding (name and address)
- Embedded X-ray images
- Doctor notes and observations
- Report expiry management (10-day default)
- Database storage with BLOB support

### Additional Features
- User authentication and session management
- Notification system (database-backed)
- Message system between patients and doctors
- Automatic expiry handling for reports, messages, and notifications
- Advanced search functionality across appointments, reports, and patients
- Date-based filtering with natural language support (e.g., "March 2024")

## Technology Stack

### Backend
- **Flask**: Web framework
- **MySQL**: Database (via mysql-connector-python)
- **TensorFlow/Keras**: Deep learning model inference
- **OpenCV (cv2)**: Image processing and Grad-CAM visualization
- **ReportLab**: PDF report generation

### Frontend
- HTML templates with Jinja2
- CSS styling
- JavaScript for interactive features

### AI/ML
- Convolutional Neural Network for X-ray classification
- Grad-CAM (Gradient-weighted Class Activation Mapping) for explainable AI
- Image preprocessing and normalization

## Prerequisites

- Python 3.x
- MySQL Server
- Virtual environment (recommended)

## Installation

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/Justinohayo/DeepChest.git
   cd DeepChest
   ```

2. **Set up virtual environment:**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirement.txt
   ```

4. **Configure MySQL database:**
   - Create a database named `DeepChest`
   - Import the schema from `DeepChest.sql`
   - Update database credentials in `app.py` if needed:
     ```python
     db_config = {
         'host': 'localhost',
         'user': 'root',
         'password': 'test1234',
         'database': 'DeepChest'
     }
     ```

5. **Ensure the AI model is present:**
   - Place `model_1.keras` in the project root directory

## Running the Application

1. **Start the Flask development server:**
   ```powershell
   .venv\Scripts\python.exe app.py
   ```

2. **Access the application:**
   - Open your browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Project Structure

```
DeepChest/
├── app.py                      # Main Flask application
├── model_1.keras               # Trained AI model
├── DeepChest.sql              # Database schema
├── requirement.txt            # Python dependencies
├── README.md                  # Project documentation
├── Kerascode.md              # Model training documentation
├── AI_Model/                  # Jupyter notebooks for model development
│   ├── DeepChest-1stModel.ipynb
│   └── Model_Run.ipynb
├── Services/                  # Service configuration files
│   ├── Ai_service.py
│   ├── DeepChest.conf
│   ├── DeepChest.service
│   └── gunicorn.service
├── static/                    # Static assets
│   ├── *.css                 # Stylesheets for different user types
│   ├── logo_DeepChest.png    # Application logo
│   └── uploads/              # User-uploaded files
├── templates/                 # HTML templates
│   ├── index.html            # Homepage
│   ├── login.html            # Login page
│   ├── signup.html           # Patient signup
│   ├── clinic_signup.html    # Clinic signup
│   ├── navigationbase.html   # Base navigation template
│   ├── search_results.html   # Search results page
│   ├── patient/              # Patient-specific templates
│   │   ├── patienthome.html
│   │   ├── p_appointments.html
│   │   ├── p_bookappointment.html
│   │   ├── p_manageappointments.html
│   │   ├── myreports.html
│   │   ├── reportdetails.html
│   │   ├── messages.html
│   │   ├── p_modifyaccount.html
│   │   ├── add-child.html
│   │   └── notifications.html
│   ├── doctor/               # Doctor-specific templates
│   │   ├── doctorhome.html
│   │   ├── doctor_appointments.html
│   │   ├── doctor_appointment_detail.html
│   │   ├── doctor_patients.html
│   │   ├── doctor_reports.html
│   │   ├── doctor_ai_diagnosis.html
│   │   ├── doctor_account.html
│   │   └── doctor_modifyaccount.html
│   └── clinic_admin/         # Clinic admin templates
│       ├── adminhome.html
│       ├── AppointmentAdmin.html
│       ├── BookAppointmentAdmin.html
│       ├── ManageAppointmentAdmin.html
│       ├── manage_clinic.html
│       ├── manage_doctor.html
│       ├── manage_patient.html
│       ├── ManageAccount.html
│       └── ManageReports.html
└── __pycache__/              # Python cache files
```

## Database Schema

The application uses MySQL with the following main tables:
- `login` - User authentication
- `patient` - Patient information
- `doctor` - Doctor information
- `clinic` - Clinic information
- `clinicadmin` - Clinic administrator details
- `appointments` - Appointment scheduling
- `Reports` - Medical reports (with BLOB storage)
- `xrays` - X-ray image storage
- `notifications` - User notifications
- `messages` - Patient-doctor messaging

## Key Routes

### Public Routes
- `/` - Homepage
- `/login` - User authentication
- `/signup` - Patient registration
- `/clinic_signup` - Clinic registration

### Patient Routes
- `/patient_home` - Patient dashboard
- `/patient/appointments` - View appointments
- `/patient/book-appointment` - Book new appointment
- `/patient/reports` - View medical reports
- `/patient/messages` - Message doctors
- `/patient/account` - Manage account

### Doctor Routes
- `/doctor_home` - Doctor dashboard
- `/doctor/appointments` - View appointments
- `/doctor/patients` - View patient list
- `/doctor/reports` - View reports
- `/doctor/ai_diagnosis` - AI diagnosis tool
- `/doctor/report_generation` - Generate PDF reports

### Admin Routes
- `/admin_home` - Admin dashboard
- `/admin/appointments` - Manage appointments
- `/admin/manage_clinic` - Clinic settings
- `/admin/manage_reports` - Report management
- `/admin/ManageAccount` - User management

## AI Model Details

The chest X-ray classification model uses:
- Input size: 224x224x3 (RGB images)
- Architecture: Convolutional Neural Network
- Output classes: 4 (COVID19, NORMAL, PNEUMONIA, TUBERCULOSIS)
- Grad-CAM layer: `last_conv` for visualization

## Authors

- Ngoc Nguyen, Theisen Reddy, Sabrina Mandla
- Repository: https://github.com/Justinohayo/DeepChest

## Acknowledgments

- TensorFlow/Keras for deep learning framework
- OpenCV for image processing capabilities
- ReportLab for PDF generation
