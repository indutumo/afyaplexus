from django.urls import path, include
from . import views

urlpatterns = [
    '''
    path('', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('user_list/', views.user_list, name='user_list'),
    path('<uuid:pk>/userdetails_edit/', views.userdetails_edit, name='userdetails_edit'),
    path('<uuid:pk>/add_userprofilerole/', views.add_userprofilerole, name='add_userprofilerole'),
    path('<uuid:pk>/remove_userrole/', views.remove_userrole, name='remove_userrole'),
    path('<uuid:pk>/activate_user/', views.activate_user, name='activate_user'),
    path('<uuid:pk>/user_detail/', views.view_profile, name='user_detail'),
    path('app/', views.app, name='app'),
    path('<int:pk>/userprofile_edit/', views.UserProfileUpdateView.as_view(), name='userprofile_edit'),
    path('change_password/', views.change_password, name='change_password'),
    path('<uuid:pk>/deactivate_user/', views.deactivate_user, name='deactivate_user'),
    path('register_user/', views.register_user, name='register_user'),
    path('send_mail_test/', views.send_mail_test, name='send_mail_test'),
    path('zolatechnologies/', views.zolatechnologies, name='zolatechnologies'),
    path('whatsapp_chat/', views.whatsapp_chat, name='whatsapp_chat'),
    path('waiter_login/', views.waiter_login, name='waiter_login'),
    path('waiter_logout/', views.waiter_logout, name='waiter_logout'),
    path('add_issue/', views.add_issue, name='add_issue'),
    path('issue_list/', views.issue_list, name='issue_list'),
    path('<uuid:pk>/add_response/', views.add_response, name='add_response'),
    path('<uuid:pk>/add_client_response/', views.add_client_response, name='add_client_response'),
    path('<uuid:pk>/issue_details/', views.IssueDetailView.as_view(), name='issue_details'),
    path('send_patient_notification/', views.send_patient_notification, name='send_patient_notification'),
    path('sms_notification_list/', views.sms_notification_list, name='sms_notification_list'),
    path('change_branch/', views.change_branch, name='change_branch'),
    path('check_username/', views.check_username, name='check_username'),
    path('change_organization/', views.change_organization, name='change_organization'),
    path('send_client_notification/', views.send_client_notification, name='send_client_notification'),
    '''
]