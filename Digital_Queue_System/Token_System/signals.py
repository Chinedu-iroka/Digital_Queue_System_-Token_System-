# Token_System/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Patient, Doctor, Department

@receiver(post_save, sender=User)
def auto_create_patient_profile(sender, instance, created, **kwargs):
    """
    Magic trick: When a User is saved, if they're a patient,
    automatically create a Patient profile for them!
    """
    if created and instance.role == 'patient':
        # Creates Patient profile linked to this User
        Patient.objects.create(
            user=instance,  
            name=instance.username,  # Use username as default name
            email=instance.email,    # Use user's email
            # date_of_birth will be copied automatically from User model
            date_of_birth=instance.date_of_birth
        )

@receiver(post_save, sender=User)
def update_patient_profile(sender, instance, **kwargs):
    """
    If user updates their info, also update their Patient profile
    """
    if instance.role == 'patient':
        try:
            patient_profile = instance.patient_profile
            patient_profile.name = instance.username
            patient_profile.email = instance.email
            patient_profile.date_of_birth = instance.date_of_birth
            patient_profile.save()
        except Patient.DoesNotExist:
            # If patient profile doesn't exist but should, create it
            Patient.objects.create(
                user=instance,
                name=instance.username,
                email=instance.email,
                date_of_birth=instance.date_of_birth
            )

@receiver(post_save, sender=User)
def auto_create_doctor_profile(sender, instance, created, **kwargs):
    """
    When a User is saved with doctor role,
    automatically create a Doctor profile for them!
    """
    if created and instance.role == 'doctor':
        
        default_department, created = Department.objects.get_or_create(
            name="General Medicine",
            defaults={'description': 'Default department for new doctors'}
        )
        
        # Doctor profile linked to this User
        Doctor.objects.create(
            user=instance,
            name=instance.username,  
            specialty="General Practice",  
            department=default_department
        )