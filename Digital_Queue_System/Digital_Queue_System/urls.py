"""
URL configuration for Digital_Queue_System project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from Token_System.views import LogoutView


def home(request):
    return HttpResponse(
        """
        <h1>🚀 Digital Queue System is live on Render!</h1>
        <p>Visit the link below to continue:</p>
        <a href="https://digital-queue-system-b8v3.onrender.com/api/" 
           style="color:blue; text-decoration:none; font-weight:bold;" target="_blank">
            👉 Go to API
        </a>
        """,
        content_type="text/html"
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home),
    path('api/', include('Token_System.urls')),
    path('api/auth/', include('allauth.urls')),
]
