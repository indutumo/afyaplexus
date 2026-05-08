from django.urls import path, include
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    #path('accounts/', include('django.contrib.auth.urls')),
]