from django.urls import path, include
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('track_click/', views.track_click, name='track_click'),
    path('track_search/', views.track_search, name='track_search'),
    path('analytics_summary/', views.analytics_summary, name='analytics_summary'),
    path('analytics_dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('visit_list', views.visit_list, name='visit_list'),
    path('pageview_list', views.pageview_list, name='pageview_list'),
    path("click_event_list/", views.click_event_list, name="click_event_list"),
    #path('accounts/', include('django.contrib.auth.urls')),
]