from django.shortcuts import render,redirect
from .forms import RegisterForm
# ,AuthenticationForm
from django.contrib.auth import login
# logout

def register_view(request):
    if request.method=="POST":
        form=RegisterForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request,user)
            
            return redirect('home')
    else:
        form=RegisterForm()
    return render(request,'accounts/register.html',{'form':form})