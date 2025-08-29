Digital Queue System - API Documentation
Base URL
text
http://127.0.0.1:8000/api/
Authentication
Token-based authentication
Get token by logging in

🔐 AUTHENTICATION ENDPOINTS
1. Register User
POST /register/
json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "role": "patient",
    "date_of_birth": "1990-01-15"
}
Roles available: admin, staff, doctor, patient
2. Login
POST /auth/login/
json
{
    "username": "johndoe",
    "password": "securepassword123"
}
Response: Returns authentication token
3. Logout
POST /auth/logout/
(Requires authentication)

👥 USER MANAGEMENT
Get All Users
GET /users/
(Admin only)
Get Specific User
GET /users/{id}/
(User can access own profile, admin can access all)
Update User
PUT/PATCH /users/{id}/
json
{
    "username": "newname",
    "email": "newemail@example.com"
}
Delete User
DELETE /users/{id}/
(Admin only)

🏥 PATIENT MANAGEMENT
Get All Patients
GET /patients/
Create Patient (or auto-created when user registers as patient)
POST /patients/
json
{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "123-456-7890",
    "date_of_birth": "1990-01-15"
}
Get Specific Patient
GET /patients/{id}/

👨‍⚕️ DOCTOR MANAGEMENT
Get All Doctors
GET /doctors/
Create Doctor (or auto-created when user registers as doctor)
POST /doctors/
json
{
    "name": "Dr. Smith",
    "specialty": "Cardiology",
    "department": 1
}

🏢 DEPARTMENT MANAGEMENT
Get All Departments
GET /departments/
Create Department
POST /departments/
json
{
    "name": "Cardiology",
    "description": "Heart disease treatment"
}

📅 APPOINTMENT MANAGEMENT
Get All Appointments
GET /appointments/
Create Appointment
POST /appointments/
json
{
    "patient": 1,
    "doctor": 1,
    "date": "2023-12-15T10:00:00Z",
    "status": "scheduled"
}
Status options: scheduled, completed, canceled

🎟️ QUEUE/TOKEN SYSTEM
Get Current Queue
GET /queues/
Shows today's queue only
Join Queue (Patient gets token number)
POST /queues/join_queue/
json
{
    "patient_id": 1
}
Call Next Token (Admin/Staff only)
POST /queues/call_next/
Mark Token as Served (Admin/Staff only)
POST /queues/{token_id}/mark_served/
Check Queue Position
GET /queues/{token_id}/position/
Reset Queue (Admin only - clears old entries)
POST /queues/reset_queue/

🔐 PERMISSIONS SUMMARY
Role
Can Access
Patient
Own profile, join queue, check position
Doctor
Own profile, view appointments
Staff
Manage queue, view most data
Admin
Everything + user management


💡 TIPS FOR USING API
Always include headers:
http
Content-Type: application/json
Authorization: Token your_token_here  # if required
Date format: Always use YYYY-MM-DD format
Time format: Use ISO format YYYY-MM-DDTHH:MM:SSZ
Check responses: Most POST requests return the created object
Error handling: Check HTTP status codes:
200 Success
201 Created
400 Bad Request (check your data)
401 Unauthorized (login required)
403 Forbidden (no permission)
404 Not Found



