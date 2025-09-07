from django.urls import path, include
from .views import PatientMedicalHistoryView, RegisterView, LoginView, LogoutView
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from allauth.account.views import PasswordResetView
from .views import (
    UserViewSet, DepartmentViewSet, DoctorViewSet,
    PatientViewSet, AppointmentViewSet, QueueViewSet, 
    RegisterView, LoginView, LogoutView, UserProfileView, 
    ChangePasswordView, MedicalRecordViewSet, PatientMedicalRecordView
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'doctors', DoctorViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'queues', QueueViewSet)
router.register(r'medical-records', MedicalRecordViewSet)

urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/password/reset/', PasswordResetView.as_view(), name='account_reset_password'),
    # path('auth/password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('patients/<int:patient_id>/medical-record/', PatientMedicalRecordView.as_view(), name='patient-medical-record'),
    path('patients/<int:patient_id>/medical-history/', PatientMedicalHistoryView.as_view(), name='patient-medical-history'),
    path('treatments/', include(router.urls)),
    path('diagnoses/', include(router.urls)),
    path('medical-notes/', include(router.urls)),
    path("", include(router.urls)),
]

urlpatterns += router.urls



# urlpatterns = [
#     path('api/', include([
#         # Auth endpoints
#         path('auth/register/', RegisterView.as_view(), name='register'),
#         path('auth/login/', LoginView.as_view(), name='login'),
#         path('auth/logout/', LogoutView.as_view(), name='logout'),
        
#         # Include router URLs under api/
#         path('', include(router.urls)),
#     ])),
# ]