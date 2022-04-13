from django.urls import path
from authapp import views

app_name = 'authapp'

urlpatterns = [
    path('registration/', views.Registration.as_view(), name='registration'),
    path('login/', views.LogIn.as_view(), name='login'),
    path('logout/', views.LogOut.as_view(), name='logout'),
    path('active/<str:email>/<int:user_otp>', views.Activate.as_view(), name='active'),
    path('resend_active/', views.ResendActivationLink.as_view(), name='resend_active'),
    path('forgot_password/', views.ForgotPassword.as_view(), name='forgot_password'),
    path('set_password/', views.SetNewPassword.as_view(), name='set_password'),
    path('change_password/', views.ChangePassword.as_view(), name='change_password')
]