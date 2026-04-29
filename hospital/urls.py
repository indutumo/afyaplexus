from django.urls import path, include
from . import views

urlpatterns = [
	path('', views.home_page, name='home_page'),
	path('<uuid:pk>/county_centre', views.county_centre, name='county_centre'),
	path('add_centre', views.add_centre, name='add_centre'),
	path('<uuid:pk>/centre_detail', views.centre_detail, name='centre_detail'),
	path('hospital_search', views.hospital_search, name='hospital_search'),
	]