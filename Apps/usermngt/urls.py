from django.urls import path
from .views import *

urlpatterns = [
    path('send-otp/', UserRegistrationView.as_view(), name='send-otp'),
    path('re-send-otp/',ResendOtpView.as_view(), name='re-send-otp'),

    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('update-user/<int:id>/', UserUpdateView.as_view(), name='update-user'),

]
