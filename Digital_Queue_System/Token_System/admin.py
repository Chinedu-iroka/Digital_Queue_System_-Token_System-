from django.contrib import admin

# Register your models here.
from .models import User, Department, Doctor, Patient, Appointment, Queue

# Simple registration without custom admin classes
admin.site.register(User)
admin.site.register(Department)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Queue)