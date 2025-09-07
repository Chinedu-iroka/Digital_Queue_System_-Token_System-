from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Appointment

@shared_task
def send_appointment_reminder(appointment_id):
    """Send reminder for a specific appointment"""
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        patient = appointment.patient
        doctor = appointment.doctor
        
        subject = f"Appointment Reminder: {appointment.date.strftime('%Y-%m-%d %H:%M')}"
        message = f"""
        Hello {patient.name},
        
        This is a reminder for your appointment with Dr. {doctor.name}
        on {appointment.date.strftime('%A, %B %d, %Y at %I:%M %p')}.
        
        Please arrive 15 minutes early.
        
        Thank you,
        {settings.SITE_NAME}
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [patient.email],
            fail_silently=False,
        )
        
        print(f"Reminder sent for appointment {appointment_id}")
        
    except Appointment.DoesNotExist:
        print(f"Appointment {appointment_id} not found")

@shared_task
def check_upcoming_appointments():
    """Check for appointments happening soon and send reminders"""
    now = timezone.now()
    reminder_time = now + timedelta(hours=24)  # 24 hours from now
    
    # Find appointments happening in the next 24 hours
    upcoming_appointments = Appointment.objects.filter(
        date__gte=now,
        date__lte=reminder_time,
        status='scheduled',
        reminder_sent=False
    )
    
    for appointment in upcoming_appointments:
        # Send reminder
        send_appointment_reminder.delay(appointment.id)
        # Mark as reminder sent
        appointment.reminder_sent = True
        appointment.save()
    
    return f"Checked {upcoming_appointments.count()} appointments"