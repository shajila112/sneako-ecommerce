from django.urls import path
from .views import (
    register_view,
    login_view,
    logout_view,
    otp_verify_view,
    resend_otp,
    forgot_password_view,
    forgot_password_otp_view,
    forgot_resend_otp,
    reset_password_view,
    reset_success_view,
    address_list_view,
    add_address_view,
    edit_address_view,
    delete_address_view,
    profile_view,
)

app_name = 'accounts'

urlpatterns = [
    # AUTH
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # REGISTER OTP
    path('otp/', otp_verify_view, name='otp_verify'),
    path('resend-otp/', resend_otp, name='resend_otp'),
    

    # FORGOT PASSWORD
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('forgot-password/otp/', forgot_password_otp_view, name='forgot_password_otp'),
    path('reset-password/', reset_password_view, name='reset_password'),
    path('forgot-password/resend-otp/',forgot_resend_otp,name='forgot_resend_otp'),
    path('reset-success/', reset_success_view, name='reset_success'),

    # ACCOUNT / PROFILE
    path('profile/', profile_view, name='profile'),
    path('addresses/', address_list_view, name='address_list'),
    path('addresses/add/', add_address_view, name='add_address'),
    path('addresses/edit/<int:pk>/', edit_address_view, name='edit_address'),
    path('addresses/delete/<int:pk>/', delete_address_view, name='delete_address'),
]

