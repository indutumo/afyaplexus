from django.urls import path, include
from . import views

urlpatterns = [
	path('', views.home_page, name='home_page'),
	path('<uuid:pk>/county_centre', views.county_centre, name='county_centre'),
	]