from django.urls import path
from . import views

urlpatterns = [
    path('blog_list/', views.blog_list, name='blog_list'),
    path('blog_detail/<uuid:pk>/', views.blog_detail, name='blog_detail'),
    path('clap/<uuid:pk>/', views.clap_post, name='clap_post'),
    path('bookmark/<uuid:pk>/', views.bookmark_post, name='bookmark_post'),
]