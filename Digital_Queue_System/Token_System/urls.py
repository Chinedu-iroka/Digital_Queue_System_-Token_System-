from django.urls import path, include
from .views import RegisterView, LoginView, LogoutView
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, DepartmentViewSet, DoctorViewSet,
    PatientViewSet, AppointmentViewSet, QueueViewSet, RegisterView, LoginView, LogoutView,
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'doctors', DoctorViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'queues', QueueViewSet)

urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
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