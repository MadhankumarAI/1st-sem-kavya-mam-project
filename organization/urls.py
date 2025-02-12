

from django.urls import path, include

from . import views

urlpatterns = [

    path('postings/', views.getpostings,name= 'postings'),
    path('', views.register,name= 'compreg'),
    path('login', views.login_view,name='complogin'),
    path('verify-email/', views.verify_email, name='compverify_email'),
    path('resend-code/', views.resend_code, name='compresend_code'),
    path('logout/', views.logoutView, name='complogout'),
    path('forgot-password/', views.forgot_password, name='compforgot_password'),
    path('verify-reset-code/', views.verify_reset_code, name='compverify_reset_code'),
    path('reset-password/', views.reset_password, name='compreset_password'),
    path('resend-reset-code/', views.resend_reset_code, name='compresend_reset_code'),
    path('createposting/',views.create_posting,name='createposting'),
    path('createinterview/',views.create_custom_interview,name='createcustominterview'),
    path('attempted/',views.Attempted,name='attempted'),
    path('chat_create-<int:post>', views.chatcreate, name='compchatcreate'),
    path('chat-<str:convoid>/', views.chat, name='compchat'),
]