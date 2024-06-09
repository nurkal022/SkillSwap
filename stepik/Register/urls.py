from django.contrib import admin
from django.urls import path, include
# from django.contrib.auth import auth_views
from .decorators import unauthenticated_user
from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    

]