from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP,CustomUser
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


from django.contrib.auth.models import User


class UserRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        # Step 1: Serialize and save user
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Step 2: Generate OTP for email verification
            otp_instance = OTP.generate_otp(user)
            otp=otp_instance.otp 

            # Step 3: Send OTP to the user's email
            send_mail(
                'Your Email Verification OTP',
                f'Your OTP code is {otp_instance.otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return Response({"message": "User registered. OTP sent to email."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
class ResendOtpView(APIView):
    
    def post(self, request, *args, **kwargs):
        # Retrieve the user email from the request
        email = request.data.get("email")
        
        # Check if the user exists
        try:
            user = CustomUser.objects.get(email=email)
            
        except CustomUser.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate a new OTP and update the expiration time
        otp = ''.join(random.choices(string.digits, k=6))  # Generate a random OTP
        expires_at = timezone.now() + timedelta(minutes=5)  # Set OTP to expire after 5 minutes
        
        # Find the existing OTP instance (if any)
        otp_instance = OTP.objects.filter(user=user).first()

        if otp_instance:
            send_mail(
            'Your Email Verification OTP',
            f'Your OTP code is {otp_instance.otp}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

            # Update the existing OTP instance (optional)
            otp_instance.otp = otp
            otp_instance.expires_at = expires_at
            otp_instance.save()
        else:
            # Create a new OTP instance if no existing one is found
            otp_instance = OTP.objects.create(user=user, otp=otp, expires_at=expires_at)


        return Response(
            {
                "message": "OTP has been regenerated successfully.",
                "otp": otp,  # You might not want to return OTP in real scenarios for security
                "expires_at": otp_instance.expires_at
            },
            status=status.HTTP_200_OK
        )





class VerifyOTPView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        otp_input = request.data.get("otp")

        user = CustomUser.objects.filter(email=email).first()

        if not user:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve OTP for the user and validate it
        try:
            otp_instance = OTP.objects.get(user=user, otp=otp_input)
            otp_instance.is_varified=True
            otp_instance.save()
        except OTP.DoesNotExist:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_instance.is_expired():
            return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "OTP verified successfully, email is now verified!","user_id": user.id}, status=status.HTTP_200_OK)
    
    
    
class UserUpdateView(APIView):
    def post(self, request, id, *args, **kwargs):
        # Retrieve the user by ID
        user = get_object_or_404(CustomUser, id=id)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()  # Save the updated user data
            return Response({"message": "User details updated successfully."}, status=status.HTTP_200_OK)
        
        # If the serializer is not valid, return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
