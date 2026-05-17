from django.urls import path
from . import views

urlpatterns = [
    path('doctor_list/', views.doctor_list, name='doctor_list'),
    path('add_doctor/', views.add_doctor, name='add_doctor'),
    path('doctor_detail/<uuid:pk>/', views.doctor_detail, name='doctor_detail'),
    path('add_partner', views.add_partner, name='add_partner'),
    path('add_volunteer', views.add_volunteer, name='add_volunteer'),
    path('add_patient', views.add_patient, name='add_patient'),
    path('partner_list', views.partner_list, name='partner_list'),
    path('patient_list', views.patient_list, name='patient_list'),
    path('volunteer_list', views.volunteer_list, name='volunteer_list'),
]