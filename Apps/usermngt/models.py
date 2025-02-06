from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.utils import timezone
from datetime import timedelta
import datetime
from django.contrib.auth.models import AbstractUser




class CustomUser(models.Model):
    user_name = models.CharField(max_length=36,blank=True,null=True)
    email = models.EmailField(unique=True)  # The 'unique=True' ensures that each email address is unique
    first_name = models.CharField(max_length=36,blank=True,null=True)
    last_name = models.CharField(max_length=36,blank=True,null=True)

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        null=True,  # Allow gender to be optional
        blank=True,  # Allow gender to be optional
    )

    # Add related_name to avoid clashes with the default User model
    
    
class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    expires_at = models.DateTimeField()
    is_varified = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.user.email}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def generate_otp(cls, user):
        otp = ''.join(random.choices(string.digits, k=6))
        expires_at = timezone.now() + timedelta(minutes=2)  # OTP expires after 5 minutes
        otp_instance = cls.objects.create(user=user, otp=otp, expires_at=expires_at)
        return otp_instance
