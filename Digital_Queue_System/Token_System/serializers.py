from rest_framework import serializers
from .models import Department, Diagnosis, Doctor, MedicalNote, Patient, Appointment, Queue, Treatment, User, MedicalRecord

# ------------------------
# User Serializer
# ------------------------
class UserSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(required=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password', 'date_of_birth']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# ------------------------
# Department Serializer
# ------------------------
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


# ------------------------
# Doctor Serializer
# ------------------------
class DoctorSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True
    )

    class Meta:
        model = Doctor
        fields = ['id', 'name', 'specialty', 'department', 'department_id']


# ------------------------
# Patient Serializer
# ------------------------
class PatientSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Patient
        fields = ['id', 'user_id', 'username', 'name', 'email', 'phone', 'date_of_birth']


# ------------------------
# Appointment Serializer
# ------------------------
class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'


# ------------------------
# Queue Serializer
# ------------------------
class QueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        fields = '__all__'

# ------------------------
# User Profile Serializer
# ------------------------
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'date_of_birth', 'first_name', 'last_name']
        read_only_fields = ['id', 'role']  # Users can't change their ID or role
        
    def validate_email(self, value):
        """ Email should be unique except for current user"""
        user = self.context['request'].user
        if User.objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
    
# ------------------------
# Medical Record Serializer
# ------------------------
class MedicalRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'patient_name', 'blood_type', 'allergies', 
            'chronic_conditions', 'current_medications', 'emergency_contact_name',
            'emergency_contact_phone', 'emergency_contact_relation', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

# ------------------------
# Treatment Serializer
# ------------------------
class TreatmentSerializer(serializers.ModelSerializer):
    prescribed_by_name = serializers.CharField(source='prescribed_by.name', read_only=True)
    
    class Meta:
        model = Treatment
        fields = '__all__'

# ------------------------
# Diagnosis Serializer
# ------------------------
class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = '__all__'

# ------------------------
# Medical Note Serializer
# ------------------------
class MedicalNoteSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    
    class Meta:
        model = MedicalNote
        fields = '__all__'

# ------------------------------------
# Patient Medical History Serializer
# -------------------------------------
class PatientMedicalHistorySerializer(serializers.ModelSerializer):
    appointments = AppointmentSerializer(many=True, read_only=True)
    treatments = TreatmentSerializer(many=True, read_only=True)
    diagnoses = DiagnosisSerializer(many=True, read_only=True)
    medical_notes = MedicalNoteSerializer(many=True, read_only=True)
    medical_record = MedicalRecordSerializer(read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'name', 'email', 'phone', 'date_of_birth',
            'appointments', 'treatments', 'diagnoses', 
            'medical_notes', 'medical_record'
        ]