from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,"products/index.html")

def shop(request):
    return render(request,'shop.html')

def shop_category(request,category):
    return render(request,'shop.html',{'category':category})