Base URL
http://localhost:8000/api/
Authentication
Most endpoints require authentication using Token authentication.
Obtain Authentication Token

POST - http://localhost:8000 /api/auth/login/
Content-Type: application/json

{
  "username": "doctor_smith",
  "password": "password123"
}
Response:
json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "doctor_smith",
    "role": "doctor"
  }
}
Include Token in Requests

Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

API Endpoints
Authentication Endpoints
Login

POST - http://localhost:8000/api/auth/login/
Authenticate user and receive token.
Logout

POST - http://localhost:8000/api/auth/logout/
Invalidate current authentication token.
Register User

POST - http://localhost:8000/api/register/
Content-Type: application/json

{
  "username": "new_user",
  "email": "user@example.com",
  "password": "securepassword123",
  "role": "patient",
  "date_of_birth": "1990-01-01"
}

User Management
Get All Users

GET -  http://localhost:8000/api/users/
Permissions: Admin only
Get User Profile

GET - http://localhost:8000/api/profile/
Get current authenticated user's profile.
Update User Profile
PUT - http://localhost:8000/api/profile/
Content-Type: application/json

{
  "email": "updated@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
Change Password

POST - http://localhost:8000/api/profile/change-password/
Content-Type: application/json

{
  "old_password": "currentpassword",
  "new_password": "newsecurepassword"
}

Department Management
Get All Departments

GET - http://localhost:8000 /api/departments/
Create Department (Admin only)

POST - http://localhost:8000/api/departments/
Content-Type: application/json

{
  "name": "Cardiology",
  "description": "Heart and cardiovascular care"
}
Get Single Department
GET - http://localhost:8000/api/departments/{id}/

Doctor Management
Get All Doctors

GET - http://localhost:8000/api/doctors/
Create Doctor (Admin only)

POST -  http://localhost:8000/api/doctors/
Content-Type: application/json

{
  "name": "Dr. Jane Smith",
  "specialty": "Cardiologist",
  "department_id": 1
}

Get Doctor Details

GET http://localhost:8000/api/doctors/{id}/

Patient Management
Get All Patients

GET - http://localhost:8000/api/patients/
Permissions: Doctors, Staff, Admin
Create Patient

POST - http://localhost:8000/api/patients/
Content-Type: application/json

{
  "name": "John Patient",
  "email": "john@example.com",
  "phone": "+1234567890",
  "date_of_birth": "1985-05-15"
}
Get Patient Details

GET - http://localhost:8000/api/patients/{id}/

Appointment Management
Get All Appointments
GET - http://localhost:8000/api/appointments/
Create Appointment

POST - http://localhost:8000/api/appointments/
Content-Type: application/json

{
  "patient_id": 1,
  "doctor_id": 1,
  "date": "2024-01-15T14:30:00Z",
  "status": "scheduled"
}
Send Appointment Reminder

POST - http://localhost:8000/api/appointments/{id}/send_reminder/
Manually send email reminder for specific appointment.
Get Upcoming Reminders

GET - http://localhost:8000/api/appointments/upcoming_reminders/
Get appointments needing reminders in next 24 hours.

Queue/Token System
Get Current Queue

GET - http://localhost:8000/api/queues/
Get today's queue entries.
Join Queue

POST - http://localhost:8000/api/queues/join_queue/
Content-Type: application/json

{
  "patient_id": 1
}
Response:
json
{
  "message": "Successfully joined the queue.",
  "token_details": {
    "id": 15,
    "patient": 1,
    "token_number": 5,
    "is_called": false,
    "is_served": false,
    "created_at": "2024-01-10T09:30:45.123456Z"
  }
}
Call Next Token

POST - http://localhost:8000/api/queues/call_next/
Call the next patient in queue.
Mark Token as Served

POST - http://localhost:8000/api/queues/{id}/mark_served/
Mark specific token as served.
Get Queue Position

GET - http://localhost:8000/api/queues/{id}/position/
Get position of a token in today's queue.
Reset Queue (Admin only)

POST - http://localhost:8000/api/queues/reset_queue/
Clear all previous day's queue entries.

Medical Records
Get Patient Medical Record

GET - http://localhost:8000/api/patients/{patient_id}/medical-record/
Permissions: Doctors, Staff, Admin
Create/Update Medical Record

POST - http://localhost:8000/api/medical-records/
Content-Type: application/json

{
  "patient": 1,
  "blood_type": "A+",
  "allergies": "Penicillin, Shellfish",
  "chronic_conditions": "Hypertension",
  "current_medications": "Lisinopril 10mg daily"
}
Get Complete Medical History

GET - http://localhost:8000/api/patients/{patient_id}/medical-history/
Response includes: Appointments, treatments, diagnoses, notes, and medical records.

Treatment Management
Get All Treatments

GET - http://localhost:8000/api/treatments/
Permissions: Medical staff only
Create Treatment

POST - http://localhost:8000/api/treatments/
Content-Type: application/json

{
  "appointment_id": 1,
  "treatment_type": "medication",
  "name": "Amoxicillin",
  "description": "Antibiotic for infection",
  "dosage": "500mg three times daily",
  "duration": "7 days",
  "start_date": "2024-01-10"
}

Diagnosis Management
Get All Diagnoses

GET - http://localhost:8000/api/diagnoses/
Permissions: Medical staff only
Create Diagnosis

POST - http://localhost:8000/api/diagnoses/
Content-Type: application/json

{
  "appointment_id": 1,
  "condition": "Upper Respiratory Infection",
  "description": "Patient presents with cough and fever",
  "severity": "moderate",
  "diagnosed_date": "2024-01-10"
}

Medical Notes
Get All Medical Notes

GET - http://localhost:8000/api/medical-notes/
Permissions: Medical staff only
Create Medical Note

POST - http://localhost:8000/api/medical-notes/
Content-Type: application/json

{
  "appointment_id": 1,
  "note_type": "progress",
  "title": "Follow-up Visit",
  "content": "Patient showing improvement with medication"
}

Filtering and Searching
Most list endpoints support filtering, searching, and ordering:
Filtering

GET - http://localhost:8000/api/users/?role=doctor&is_active=true
GET - http://localhost:8000/api/appointments/?status=scheduled&doctor=1
Searching

GET - http://localhost:8000/api/users/?search=john
GET - http://localhost:8000/api/patients/?search=email@example.com
Ordering

GET - http://localhost:8000/api/appointments/?ordering=-date
GET - http://localhost:8000/api/queues/?ordering=token_number

Error Responses
Common HTTP Status Codes
200 OK - Successful request
201 Created - Resource created successfully
400 Bad Request - Invalid input data
401 Unauthorized - Authentication required
403 Forbidden - Insufficient permissions
404 Not Found - Resource not found
500 Internal Server Error - Server error
Error Response Format
json
{
  "error": "Error message description",
  "details": {
    "field_name": ["Specific error message"]
  }
}

Example Usage Scenarios
1. Patient Registration and Queue Join

1. Register patient
POST http://localhost:8000/api/register/
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "patient",
  "date_of_birth": "1980-05-15"
}

2. Login
POST http://localhost:8000/api/auth/login/
{
  "username": "john_doe",
  "password": "password123"
}

3. Join queue
POST http://localhost:8000/api/queues/join_queue/
{
  "patient_id": 1
}
2. Doctor Managing Appointments

1. Login as doctor
POST http://localhost:8000 /api/auth/login/
{
  "username": "dr_smith",
  "password": "doctorpass"
}

 2. View today's appointments
GET http://localhost:8000/api/appointments/?date__gte=2024-01-10

3. Create diagnosis after appointment
POST http://localhost:8000/api/diagnoses/
{
  "appointment_id": 15,
  "condition": "Hypertension",
  "description": "Prescribed medication and lifestyle changes",
  "severity": "moderate"
}
3. Administrative Tasks

1. View all users
GET http://localhost:8000/api/users/

 2. Create new department
POST http://localhost:8000/api/departments/
{
  "name": "Neurology",
  "description": "Brain and nervous system care"
}

3. Reset daily queue
POST http://localhost:8000/api/queues/reset_queue/

Setup and Installation
Clone and install dependencies:
bash
pip install -r requirements.txt
Run migrations:
bash
python manage.py migrate
Start development server:
bash
python manage.py runserver
Start Celery worker (for background tasks):
bash
celery -A Digital_Queue_System worker --loglevel=info
Start Redis (required for Celery):
bash
docker run -d -p 6379:6379 --name redis redis:alpine

Testing the API
Use 
Postman - API testing and development
