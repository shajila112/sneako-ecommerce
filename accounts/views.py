from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
import random
from django.core.mail import send_mail
from .models import EmailOTP
from django.conf import settings


def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm_password')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('accounts:register')

        if User.objects.filter(username=email).exists():
            messages.error(request, "User already registered. Please login.")
            return redirect('accounts:login')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            is_active=False
        )
        user.first_name = name
        user.save()

        otp=str(random.randint(1000,9999))
        EmailOTP.objects.update_or_create (user=user,defaults={'otp':otp})

        send_mail(subject="Your SNEAKO OTP",
        message=f"Your OTP is {otp}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,)
        
        request.session['otp_user_id']=user.id 
        return redirect('accounts:otp')

    return render(request, 'accounts/register.html')

        


    

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return redirect('store:home')
        else:
            messages.error(request, "Invalid email or password")

    return render(request, 'accounts/login.html')

       


def logout_view(request):
    logout(request)
    return redirect('home')


def otp_verify_view(request):
    user_id=request.session.get('otp_user_id')

    if not user_id:
        return redirect('accounts:register')
    
    user=User.objects.get(id=user_id)

    if request.method=='POST':
        otp_entered=(
            request.POST.get('otp1')+
            request.POST.get('otp2')+
            request.POST.get('otp3')+
            request.POST.get('otp4')
        )

        otp_obj=EmailOTP.objects.get(user=user)

        if otp_obj.otp==otp_entered:
            user.is_active=True
            user.save()
            otp_obj.delete()
            login(request,user)
            return redirect('store:home')
        else:
            messages.error(request,"Invalid OTP")
    return render(request,'accounts/otp_verify.html')






    

    