from django.shortcuts import render

# Create your views here.
from rest_framework import generics
# from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
from django.db.models import Max
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .models import Diagnosis, MedicalNote, Treatment, User
from rest_framework import filters
from .tasks import send_appointment_reminder
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
from .filters import UserFilter
from django.utils.decorators import method_decorator
from rest_framework.authtoken.models import Token
from .models import Department, Doctor, Patient, Appointment, Queue, MedicalRecord
from .serializers import (
    DepartmentSerializer, DiagnosisSerializer, DoctorSerializer, MedicalNoteSerializer, PatientSerializer,
    AppointmentSerializer, QueueSerializer, TreatmentSerializer, UserSerializer, 
    UserProfileSerializer, MedicalRecordSerializer
)

# Generic ViewSets for CRUD

# ------------------------
# Register Viewset
# ------------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []

# --------------------------------------------------
# User ViewSet, including search fields and filter 
# --------------------------------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Search fields - for general text search
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    # Filter fields - for exact field matching
    filterset_fields = ['role', 'is_active']
    
    # Ordering fields - for sorting
    ordering_fields = ['username', 'email', 'date_joined', 'last_login']
    ordering = ['username']  # Default ordering


# ------------------------
# Department ViewSet
# ------------------------
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

# ------------------------
#Doctor ViewSet
# ------------------------
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

# ------------------------
#Patient ViewSet
# ------------------------
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

# ------------------------
# Appointment ViewSet
# ------------------------
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    @action(detail=True, methods=['post'], url_path='send_reminder', url_name='send_reminder')
    def send_reminder(self, request, pk=None):
        """Manual endpoint to send reminder for specific appointment"""
        appointment = self.get_object()
        
        # Send reminder using Celery task
        send_appointment_reminder.delay(appointment.id)
        
        # Update reminder status
        appointment.reminder_sent = True
        appointment.save()
        
        return Response({
            "message": f"Reminder sent for appointment {appointment.id}",
            "patient": appointment.patient.name,
            "date": appointment.date
        })
    
    @action(detail=False, methods=['get'])
    def upcoming_reminders(self, request):
        """Get appointments needing reminders"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        next_24h = now + timedelta(hours=24)
        
        appointments = Appointment.objects.filter(
            date__gte=now,
            date__lte=next_24h,
            status='scheduled',
            reminder_sent=False
        )
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

# ------------------------
# Logout View
# ------------------------

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Delete the token for the current user
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            return Response({"error": "No active token found."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

# ------------------------
# Login View
# ------------------------

class LoginView(APIView):
    permission_classes = []  # Allow anyone to try login

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role if hasattr(user, "role") else None
            }
        }, status=status.HTTP_200_OK)



# ------------------------
# Queue ViewSet
# ------------------------
class QueueViewSet(viewsets.ModelViewSet):
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer

    # Custom Action 1: Join the Queue (Auto-generate Token)
    @action(detail=False, methods=['post'])
    def join_queue(self, request):
        """
        Allows a patient to join the queue. Automatically assigns the next token number for the day.
        Expects 'patient_id' in request data.
        """
        patient_id = request.data.get('patient_id')
        
        # Validate that patient_id is provided
        if not patient_id:
            return Response({"error": "patient_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Get today's date
        today = timezone.now().date()
        today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        today_end = timezone.make_aware(datetime.combine(today, datetime.max.time()))

        # Find the maximum token number issued today
        last_token_today = Queue.objects.filter(
            created_at__range=(today_start, today_end)
        ).aggregate(Max('token_number'))['token_number__max']

        # Calculate the next token number
        if last_token_today is None:
            next_token = 1
        else:
            next_token = last_token_today + 1

        # Create the new queue entry
        queue_entry = Queue.objects.create(
            patient=patient,
            token_number=next_token,
            is_called=False,
            is_served=False
        )

        serializer = QueueSerializer(queue_entry)
        return Response({
            "message": "Successfully joined the queue.",
            "token_details": serializer.data
        }, status=status.HTTP_201_CREATED)

    # Custom Action 2: Call the Next Token
    @action(detail=False, methods=['post'])
    def call_next(self, request):
        """
        Admin action: Calls the next token in the queue (the oldest uncalled token).
        """
        # Get today's date
        today = timezone.now().date()
        today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))

        # Find the next token (lowest number, not called, not served, from today)
        next_in_line = Queue.objects.filter(
            created_at__gte=today_start,
            is_called=False,
            is_served=False
        ).order_by('token_number').first()

        if not next_in_line:
            return Response({"message": "The queue is empty."}, status=status.HTTP_200_OK)

        # Update the token status to 'called'
        next_in_line.is_called = True
        next_in_line.save()

        serializer = QueueSerializer(next_in_line)
        return Response({
            "message": "Next token called.",
            "called_token": serializer.data
        }, status=status.HTTP_200_OK)

    # Custom Action 3: Mark a Token as Served
    @action(detail=True, methods=['post'])
    def mark_served(self, request, pk=None):
        """
        Admin action: Marks a specific token as served.
        Uses the token's ID (pk) from the URL.
        """
        try:
            queue_entry = self.get_object() # Gets the Queue object based on the ID in the URL
        except Queue.DoesNotExist:
            return Response({"error": "Token not found."}, status=status.HTTP_404_NOT_FOUND)

        if queue_entry.is_served:
            return Response({"message": "Token was already marked as served."}, status=status.HTTP_200_OK)

        queue_entry.is_served = True
        queue_entry.save()

        serializer = QueueSerializer(queue_entry)
        return Response({
            "message": "Token successfully marked as served.",
            "served_token": serializer.data
        }, status=status.HTTP_200_OK)

    # Custom Action 4: Reset the Queue (Daily)
    @action(detail=False, methods=['post'])
    def reset_queue(self, request):
        """
        ADMIN ONLY: Deletes all queue entries from previous days.
        This should be called once per day to start fresh.
        """
        # Get today's date
        today = timezone.now().date()
        today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))

        # Delete all queue entries created BEFORE today
        old_entries = Queue.objects.filter(created_at__lt=today_start)
        delete_count, _ = old_entries.delete() # Returns (number_deleted, dict_per_model)

        return Response({
            "message": f"Queue reset successfully. Deleted {delete_count} old entries."
        }, status=status.HTTP_200_OK)

    # also override the default 'list' to show today's queue by default
    def list(self, request, *args, **kwargs):
        """
        Optionally, you can modify the main GET /api/queues/ to only show today's entries.
        """
        # Get today's date
        today = timezone.now().date()
        today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))

        # Filter the queryset for today's entries
        self.queryset = Queue.objects.filter(created_at__gte=today_start)
        return super().list(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def position(self, request, pk=None):
        """
        Returns the position of this token in today's queue.
        """
        try:
            queue_entry = self.get_object()
        except Queue.DoesNotExist:
            return Response({"error": "Token not found."}, status=status.HTTP_404_NOT_FOUND)

        if queue_entry.is_served:
            return Response({"message": "This token has already been served."}, status=status.HTTP_200_OK)

        # Get today's date
        today = timezone.now().date()
        today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))

        # Count how many unserved, uncalled tokens have a smaller token_number
        ahead = Queue.objects.filter(
            created_at__gte=today_start,
            is_called=False,
            is_served=False,
            token_number__lt=queue_entry.token_number
        ).count()

        return Response({
            "token_number": queue_entry.token_number,
            "people_ahead": ahead,
        }, status=status.HTTP_200_OK)
    

# ------------------------
# Password Reset View
# ------------------------
class PasswordResetView(APIView):
    permission_classes = []
    
    def post(self, request):
        form = PasswordResetForm(request.data)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                email_template_name='account/password_reset_email.html'
            )
            return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    

# ------------------------
# User Profile View
# ------------------------

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current user's profile"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update current user's profile"""
        serializer = UserProfileSerializer(
            request.user, 
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        """Partially update current user's profile"""
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# ------------------------
# Change Password View
# ------------------------

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        # Validate required fields
        if not old_password or not new_password:
            return Response(
                {"error": "Both old_password and new_password are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify old password
        if not user.check_password(old_password):
            return Response(
                {"error": "Wrong old password"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return Response({"message": "Password updated successfully"})
    
# ------------------------
# Medical Record ViewSet
# ------------------------
class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated]
    queryset = MedicalRecord.objects.all()
    
    def get_queryset(self):
        # Patients can only see their own records
        # Doctors/staff can see all records
        if self.request.user.role in ['doctor', 'staff', 'admin']:
            return MedicalRecord.objects.all()
        elif self.request.user.role == 'patient':
            # Get patient profile for the current user
            try:
                patient = self.request.user.patient_profile
                return MedicalRecord.objects.filter(patient=patient)
            except Patient.DoesNotExist:
                return MedicalRecord.objects.none()
        return MedicalRecord.objects.none()
    
    def perform_create(self, serializer):
        
        serializer.save()

# ----------------------------
# Patient Medical RecordView
# -----------------------------
class PatientMedicalRecordView(APIView):
    """Get medical record for a specific patient (for doctors)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, patient_id):
        if request.user.role not in ['doctor', 'staff', 'admin']:
            return Response(
                {"error": "Only medical staff can access patient records"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            patient = Patient.objects.get(id=patient_id)
            medical_record = MedicalRecord.objects.get(patient=patient)
            serializer = MedicalRecordSerializer(medical_record)
            return Response(serializer.data)
        except Patient.DoesNotExist:
            return Response(
                {"error": "Patient not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except MedicalRecord.DoesNotExist:
            return Response(
                {"error": "Medical record not found for this patient"},
                status=status.HTTP_404_NOT_FOUND
            )
        
# ----------------------------
# Patient Medical History View
# -----------------------------
class PatientMedicalHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, patient_id):
        # Check if user has permission to view medical history
        if request.user.role not in ['doctor', 'staff', 'admin']:
            return Response(
                {"error": "Only medical staff can access patient medical history"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            patient = Patient.objects.get(id=patient_id)
            
            # Get all related data
            appointments = Appointment.objects.filter(patient=patient).order_by('-date')
            treatments = Treatment.objects.filter(appointment__patient=patient)
            diagnoses = Diagnosis.objects.filter(appointment__patient=patient)
            notes = MedicalNote.objects.filter(appointment__patient=patient)
            
            data = {
                'patient': {
                    'id': patient.id,
                    'name': patient.name,
                    'email': patient.email,
                    'phone': patient.phone,
                    'date_of_birth': patient.date_of_birth
                },
                'appointments': AppointmentSerializer(appointments, many=True).data,
                'treatments': TreatmentSerializer(treatments, many=True).data,
                'diagnoses': DiagnosisSerializer(diagnoses, many=True).data,
                'medical_notes': MedicalNoteSerializer(notes, many=True).data,
                'medical_record': MedicalRecordSerializer(patient.medical_record).data if hasattr(patient, 'medical_record') else None
            }
            
            return Response(data)
            
        except Patient.DoesNotExist:
            return Response(
                {"error": "Patient not found"},
                status=status.HTTP_404_NOT_FOUND
            )

# ----------------------------
# Treatment ViewSet
# -----------------------------
class TreatmentViewSet(viewsets.ModelViewSet):
    serializer_class = TreatmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role in ['doctor', 'staff', 'admin']:
            return Treatment.objects.all()
        return Treatment.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(prescribed_by=self.request.user.doctor_profile)

# ----------------------------
# Diagnosis ViewSet
# -----------------------------
class DiagnosisViewSet(viewsets.ModelViewSet):
    serializer_class = DiagnosisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role in ['doctor', 'staff', 'admin']:
            return Diagnosis.objects.all()
        return Diagnosis.objects.none()

# ----------------------------
# Medical Note ViewSet
# -----------------------------
class MedicalNoteViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalNoteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role in ['doctor', 'staff', 'admin']:
            return MedicalNote.objects.all()
        return MedicalNote.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.doctor_profile)