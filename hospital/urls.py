from django.urls import path, include
from . import views
from django.views.generic import TemplateView


urlpatterns = [
	path('', views.home_page, name='home_page'),
	path('<uuid:pk>/county_centre', views.county_centre, name='county_centre'),
	path('add_centre', views.add_centre, name='add_centre'),
	path('<uuid:pk>/centre_detail', views.centre_detail, name='centre_detail'),
	path('hospital_search', views.hospital_search, name='hospital_search'),
	path('about_us', views.about_us, name='about_us'),
    path('terms/', TemplateView.as_view(template_name="hospital/terms.html"), name='terms'),
    path('privacy/', TemplateView.as_view(template_name="hospital/privacy.html"), name='privacy'),
    path('donate/', TemplateView.as_view(template_name="hospital/get_involved.html"), name='donate'),
    path('appointment_list', views.appointment_list, name='appointment_list'),
    path('<uuid:pk>/add_appointment', views.add_appointment, name='add_appointment'),
    path('hospital_list', views.hospital_list, name='hospital_list'),
	]