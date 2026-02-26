from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout

from.utils import generate_otp
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth.models import User
import random
from django.core.mail import send_mail
from .models import EmailOTP
from django.conf import settings


@never_cache
def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('adminpanel:admin_dashboard')
        return redirect('store:home')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not full_name:
            messages.error(request, "Full name is required")
            return redirect('accounts:register')

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
            first_name=full_name,
            is_active=False
        )

        otp = generate_otp()
        EmailOTP.objects.update_or_create(user=user, defaults={'otp': otp})

        send_mail(
            subject="Your SNEAKO OTP",
            message=f"Your OTP is {otp}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        request.session['otp_user_id'] = user.id
        messages.success(request, "OTP sent to your email")
        return redirect('accounts:otp_verify')

    return render(request, 'accounts/register.html')



        


    

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('adminpanel:admin_dashboard')
        return redirect('store:home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user:
            if not user.is_active:
                messages.error(request,"please verify OTP first ")
                return redirect('accounts:register')
           
            login(request,user)
                
        #admin vs user check
            if user.is_staff:
                return redirect('adminpanel:admin_dashboard')
            else:
                return redirect('store:home')        
        else:
            messages.error(request, "Invalid email or password")

    return render(request, 'accounts/login.html')

       


@never_cache
def logout_view(request):
    logout(request)
    return redirect('store:home')


@never_cache
def otp_verify_view(request):
    user_id=request.session.get('otp_user_id')

    if not user_id:
        return redirect('accounts:register')
    
    try:
        user=User.objects.get(id=user_id)
        otp_obj = EmailOTP.objects.get(user=user)
    except (User.DoesNotExist , EmailOTP.DoesNotExist):
        messages.error(request,"User not found.")
        return redirect('accounts:register')
    
    

    if request.method=='POST':
        otp_entered = (
        request.POST.get('otp1', '') +
        request.POST.get('otp2', '') +
        request.POST.get('otp3', '') +
        request.POST.get('otp4', '')
    )

        if otp_entered == otp_obj.otp:
            user.is_active = True
            user.save()
            otp_obj.delete()
            request.session.pop('otp_user_id', None)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(request, "Account verified successfully")
            return redirect('store:home')
        else:
            messages.error(request, "Invalid OTP")

    return render(request, 'accounts/otp_verify.html')
     

@never_cache
def resend_otp(request):
    user_id=request.session.get('otp_user_id')

    if not user_id:
        return redirect('accounts:register')
    try:
        user=User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('accounts:register')

    otp=generate_otp()
    
    

    EmailOTP.objects.update_or_create(user=user,defaults={'otp':otp})

    send_mail(
        subject="Your NEW SNEAKO OTP",
        message=f"Your new OTP is {otp}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,)

    messages.success(request,"A new OTP has been sent to your email.")
    return redirect('accounts:otp_verify')


@never_cache
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        user = User.objects.filter(email=email).first()
        if not user:
            messages.error(request, "Email not registered.")
            return redirect('accounts:forgot_password')

        otp = generate_otp()
        EmailOTP.objects.update_or_create(
            user=user,
            defaults={'otp': otp}
        )

        send_mail(
            "SNEAKO Password Reset OTP",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        request.session['reset_user_id'] = user.id
        messages.success(request, "OTP sent to your email.")
        return redirect('accounts:forgot_password_otp')

    return render(request, 'accounts/forgot_password.html')



    


@never_cache
def forgot_password_otp_view(request):
    user_id=request.session.get('reset_user_id')
    if not user_id:
        return redirect('accounts:forgot_password')
    user=User.objects.get(id=user_id)
    otp_obj=EmailOTP.objects.get(user=user)
    if request.method=='POST':
        otp_entered=(
            request.POST.get('otp1')+
            request.POST.get('otp2')+
            request.POST.get('otp3')+
            request.POST.get('otp4')
        )

        if otp_entered==otp_obj.otp:
            otp_obj.delete()
            request.session['otp_verified']=True
            return redirect('accounts:reset_password')
        else:
            messages.error(request,'invalid OTP')
    return render(request,'accounts/forgot_password_otp.html')

@never_cache
def reset_password_view(request):
    user_id = request.session.get('reset_user_id')
    otp_verified = request.session.get('otp_verified')

    if not user_id or not otp_verified:
        messages.error(request, "Unauthorized access.")
        return redirect('accounts:forgot_password')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')

        if p1 != p2:
            messages.error(request, "Passwords do not match.")
            return redirect('accounts:reset_password')

        user.set_password(p1)
        user.save()

        # clear session AFTER successful reset
        request.session.flush()

        return redirect('accounts:reset_success')

    return render(request, 'accounts/reset_password.html')


@never_cache
def forgot_resend_otp(request):
    user_id = request.session.get('reset_user_id')

    if not user_id:
        messages.error(request, "Session expired. Try again.")
        return redirect('accounts:forgot_password')

    user = User.objects.get(id=user_id)

    otp = generate_otp()
    EmailOTP.objects.update_or_create(user=user, defaults={'otp': otp})

    send_mail(
        "SNEAKO Password Reset OTP",
        f"Your new OTP is {otp}",
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )

    messages.success(request, "New OTP sent to your email.")
    return redirect('accounts:forgot_password_otp')



@never_cache
def reset_success_view(request):
    return render(request, 'accounts/reset_success.html')



from django.contrib.auth.decorators import login_required
from .forms import UserAddressForm, UserUpdateForm, UserProfileForm
from .models import UserAddress, UserProfile

@never_cache
@login_required(login_url='accounts:login')
def profile_view(request):
    user_form = UserUpdateForm(instance=request.user)
    profile_form = UserProfileForm(instance=request.user.profile)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile.html', context)

@never_cache
@login_required(login_url='accounts:login')
def address_list_view(request):
    addresses = UserAddress.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    return render(request, 'accounts/address_list.html', {'addresses': addresses})

@never_cache
@login_required(login_url='accounts:login')
def add_address_view(request):
    if request.method == 'POST':
        form = UserAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully.")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:address_list')
    else:
        form = UserAddressForm()
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Add New Address'})

@never_cache
@login_required(login_url='accounts:login')
def edit_address_view(request, pk):
    address = UserAddress.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        form = UserAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect('accounts:address_list')
    else:
        form = UserAddressForm(instance=address)
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Edit Address'})

@never_cache
@login_required(login_url='accounts:login')
def delete_address_view(request, pk):
    address = UserAddress.objects.get(pk=pk, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect('accounts:address_list')