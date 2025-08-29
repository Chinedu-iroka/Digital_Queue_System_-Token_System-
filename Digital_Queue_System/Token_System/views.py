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
from .models import User
from django.utils.decorators import method_decorator
from rest_framework.authtoken.models import Token
from .models import Department, Doctor, Patient, Appointment, Queue
from .serializers import (
    DepartmentSerializer, DoctorSerializer, PatientSerializer,
    AppointmentSerializer, QueueSerializer, UserSerializer
)

# Generic ViewSets for CRUD

# @method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Delete the token for the current user
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            return Response({"error": "No active token found."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

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

# class QueueViewSet(viewsets.ModelViewSet):
#     queryset = Queue.objects.all()
#     serializer_class = QueueSerializer

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