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
    )
    role = models.CharField(max_length=20, choices=ROLES, default='staff')

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
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="doctors")

    def __str__(self):
        return f"Dr. {self.name} ({self.specialty})"


# ------------------------
# Patient
# ------------------------
class Patient(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name


# ------------------------
# Appointment
# ------------------------
class Appointment(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    def __str__(self):
        return f"Appointment for {self.patient.name} with {self.doctor.name} on {self.date}"


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