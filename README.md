🏥 Digital Queue System
A comprehensive healthcare management system that digitizes patient flow and medical appointment scheduling through token-based queue management.

🌟 Features
Role-Based Access Control: Four user roles (Patient, Doctor, Staff, Admin)

Digital Token System: Automated queue management with real-time tracking

Appointment Scheduling: Complete appointment lifecycle management

Department Management: Organized healthcare service categorization

RESTful API: Fully functional API endpoints for all operations

Admin Dashboard: Django admin interface for system management

🚀 API Endpoints
Endpoint	Method	Description
/api/register/	POST	User registration
/api/auth/login/	POST	User authentication
/api/auth/logout/	POST	User logout
/api/users/	GET, POST	User management
/api/patients/	GET, POST	Patient records
/api/doctors/	GET, POST	Doctor management
/api/departments/	GET, POST	Department management
/api/appointments/	GET, POST	Appointment scheduling
/api/queues/join_queue/	POST	Join patient queue
/api/queues/call_next/	POST	Call next token
/api/queues/{id}/mark_served/	POST	Mark token as served
🛠️ Installation
Clone the repository

bash
git clone <your-repo-url>
cd Digital_Queue_System
Create virtual environment

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Run migrations

bash
python manage.py makemigrations
python manage.py migrate
Create superuser

bash
python manage.py createsuperuser
Start development server

bash
python manage.py runserver

👥 User Roles
Patients: Can join queues, view appointments, check queue position

Doctors: Can view their appointments and patient details

Staff: Can manage queues, appointments, and basic operations

Admins: Full system access and user management

🔧 Technology Stack
Backend: Django 5.2, Django REST Framework

Database: SQLite (Development), PostgreSQL (Production-ready)

Authentication: Token-based authentication

API Documentation: Built-in DRF browsable API

📋 Models Overview
User: Custom user model with role-based permissions

Patient: Patient records and medical information

Doctor: Doctor profiles with specialty and department assignment

Department: Healthcare service categories

Appointment: Scheduling system with status tracking

Queue: Token-based queue management system

🚦 Queue System Workflow
Patient registers or logs into the system

Patient joins queue receiving a digital token

Staff members call next tokens in sequence

Doctors serve patients based on token order

Tokens are marked as served upon completion

Daily queue reset maintains system cleanliness

🌐 Usage Examples
User Registration
bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johnpatient",
    "email": "john@example.com",
    "password": "securepassword123",
    "role": "patient",
    "date_of_birth": "1990-01-15"
  }'
Join Queue
bash
curl -X POST http://127.0.0.1:8000/api/queues/join_queue/ \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1}'


Built with Django REST Framework - Making healthcare management efficient and digital! 🏥💻
