from django.urls import path, include
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('track_click/', views.track_click, name='track_click'),
    path('track_search/', views.track_search, name='track_search'),
    path('analytics_summary/', views.analytics_summary, name='analytics_summary'),
    path('analytics_dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    #path('accounts/', include('django.contrib.auth.urls')),
]