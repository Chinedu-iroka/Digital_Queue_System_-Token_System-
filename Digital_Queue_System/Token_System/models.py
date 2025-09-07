from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

# ------------------------
# Custom User Model
# ------------------------
class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('doctor', 'Doctor'),
        ('patient', 'patient'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='staff')
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
# ------------------------
# Department
# ------------------------
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# ------------------------
# Doctor
# ------------------------
class Doctor(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True,  # Allow null temporarily
        blank=True,
        related_name='doctor_profile'  # This lets us do user.doctor_profile
    )
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="doctors")

    def __str__(self):
        return f"Dr. {self.name} ({self.specialty})"


# ------------------------
# Patient
# ------------------------
class Patient(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True,  # Allow null temporarily for existing data
        blank=True,
        related_name='patient_profile'
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField()

    def __str__(self):
        return self.name


# ------------------------
# Queue / Token System
# ------------------------
class Queue(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="queue_entries")
    token_number = models.IntegerField()
    is_called = models.BooleanField(default=False)
    is_served = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['token_number']

    def __str__(self):
        return f"Token {self.token_number} - {self.patient.name}"
    
# ------------------------
# MedicalRecord
# ------------------------
class MedicalRecord(models.Model):
        BLOOD_TYPE_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )
    
        patient = models.OneToOneField(
        Patient, 
        on_delete=models.CASCADE, 
        related_name='medical_record'
    )
        blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True, null=True)
        allergies = models.TextField(blank=True, null=True, help_text="List of allergies")
        chronic_conditions = models.TextField(blank=True, null=True, help_text="Chronic medical conditions")
        current_medications = models.TextField(blank=True, null=True, help_text="Current medications")
        emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
        emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
        emergency_contact_relation = models.CharField(max_length=50, blank=True, null=True)
        notes = models.TextField(blank=True, null=True, help_text="Additional medical notes")
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        def __str__(self):
            return f"Medical Record - {self.patient.name}"


# ------------------------
# Appointment
# ------------------------
class Appointment(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'), 
        ('canceled', 'Canceled'),
        ('no_show', 'No Show'),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    reminder_sent = models.BooleanField(default=False)  # For appointment reminders
    
    def __str__(self):
        return f"Appointment for {self.patient.name} with {self.doctor.name} on {self.date}"
    

# ------------------------
# Patient Medical History
# ------------------------
class Treatment(models.Model):
    TREATMENT_TYPES = (
        ('medication', 'Medication'),
        ('therapy', 'Therapy'),
        ('surgery', 'Surgery'),
        ('procedure', 'Procedure'),
        ('other', 'Other'),
    )
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="treatments")
    treatment_type = models.CharField(max_length=20, choices=TREATMENT_TYPES)
    name = models.CharField(max_length=200)
    description = models.TextField()
    dosage = models.CharField(max_length=100, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    prescribed_by = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} for {self.appointment.patient.name}"


# ------------------------
# Diagnosis
# ------------------------
class Diagnosis(models.Model):
    SEVERITY_CHOICES = (
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('critical', 'Critical'),
    )
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="diagnoses")
    condition = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='mild')
    diagnosed_date = models.DateField()
    resolved = models.BooleanField(default=False)
    resolved_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.condition} - {self.appointment.patient.name}"



# ------------------------
# MedicalNote
# ------------------------
class MedicalNote(models.Model):
    NOTE_TYPES = (
        ('progress', 'Progress Note'),
        ('consultation', 'Consultation Note'),
        ('discharge', 'Discharge Summary'),
        ('procedure', 'Procedure Note'),
        ('other', 'Other'),
    )
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="notes")
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.appointment.patient.name}"