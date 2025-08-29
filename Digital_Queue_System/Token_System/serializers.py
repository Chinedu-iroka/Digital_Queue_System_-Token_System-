from rest_framework import serializers
from .models import Department, Doctor, Patient, Appointment, Queue, User

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