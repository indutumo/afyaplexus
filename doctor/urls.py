from django.urls import path
from . import views

urlpatterns = [
    path('doctor_list/', views.doctor_list, name='doctor_list'),
    path('add_doctor/', views.add_doctor, name='add_doctor'),
    path('doctor_detail/<uuid:pk>/', views.doctor_detail, name='doctor_detail'),
]