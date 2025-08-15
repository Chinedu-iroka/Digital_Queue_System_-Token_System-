from rest_framework import routers
from .views import (
    UserViewSet, DepartmentViewSet, DoctorViewSet,
    PatientViewSet, AppointmentViewSet, QueueViewSet
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'doctors', DoctorViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'queues', QueueViewSet)

urlpatterns = router.urls