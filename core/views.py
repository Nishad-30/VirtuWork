from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from simulation.models import Simulation
from evaluation.models import ProgressReport
def landing_page(request):
    return render(request,"index.html")

def check_email_exists(request):
    
    email = request.GET.get('email', None)
    data = {
        'exists': User.objects.filter(email__iexact=email).exists()
    }
    return JsonResponse(data)

def signup_view(request):
    if request.method == "POST":
        # Capture from your existing frontend fields
        data = request.POST
        if data['password'] != data['confirm_password']:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})
        
        if User.objects.filter(username=data['username']).exists():
            return render(request, 'signup.html', {'error': 'Username taken'})

        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        # Create the profile for education info
        UserProfile.objects.create(user=user)
        login(request, user)
        return redirect('dashboard')
    
    return render(request, 'signup.html')

def login_view(request):
    if request.method == "POST":
        # Use email as the identifier
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Standard Django auth usually uses username, 
        # so we find the username associated with that email first
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
        except User.DoesNotExist:
            pass
            
        return render(request, 'login.html', {'error': 'Invalid Credentials'})
    
    return render(request, 'login.html')



@login_required
def dashboard_view(request):
    simulations = Simulation.objects.filter(user=request.user).order_by('-created_at')
    # Get the latest report for the summary box
    last_report = ProgressReport.objects.filter(simulation__user=request.user).last()
    
    context = {
        'simulations': simulations,
        'last_completed_report': last_report
    }
    return render(request, 'dashboard.html', context)


def how_it_works(request):
    return render(request, "explain.html")











