from django.contrib import admin

# imported models here.
from .models import Diagnosis, MedicalNote, Treatment, User, Department, Doctor, Patient, Appointment, Queue

# my Simple admin registration
admin.site.register(User)
admin.site.register(Department)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Queue)
admin.site.register(Treatment)
admin.site.register(Diagnosis)
admin.site.register(MedicalNote)