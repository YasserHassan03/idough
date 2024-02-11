from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import RaspberryPi
from .forms import UserRegistrationForm, UserAuthenticationForm
import subprocess

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = UserAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def home(request):
    temperature = 25.5
    proximity = 10
    current_time = 80
    user_raspberries = RaspberryPi.objects.filter(user=request.user)

    context = {
        'temperature': temperature,
        'proximity': proximity,
        'current_time': current_time,
        'user_raspberries': user_raspberries
    }
    
    return render(request, 'home.html', context)

@login_required
def register_raspberry(request):
    if request.method == 'POST':
        raspberry_id = request.POST.get('raspberry_id')
        microservice_port = request.POST.get('microservice_port')
        # Check if the Raspberry Pi ID is in the database
        raspberry = RaspberryPi.objects.filter(id=raspberry_id).first()
        if not raspberry:
            return render(request, 'registration/register_raspberry.html', {'error': 'Invalid Raspberry Pi ID'})
        # Check if the Raspberry Pi is already registered
        if raspberry.user:
            return render(request, 'registration/register_raspberry.html', {'error': 'Raspberry Pi already registered'})
        # Register the Raspberry Pi to the current user
        raspberry.user = request.user
        if microservice_port is not None:
            raspberry.microservice_port = microservice_port
            subprocess.Popen(["python3", "../../AWS-STUFF/app.py", str(microservice_port)])

        raspberry.save()
        return redirect('home')
    else:
        return render(request, 'registration/register_raspberry.html')
    
def get_microservice_port(request, raspberry_id):
    try:
        raspberry_pi = RaspberryPi.objects.get(id=raspberry_id)
        if raspberry_pi.microservice_port is None:
            return JsonResponse({'error': 'Microservice port is not set'})
        return JsonResponse({'microservice_port': raspberry_pi.microservice_port})
    except RaspberryPi.DoesNotExist:
        return JsonResponse({'error': 'Raspberry Pi not found'})

def default_route(request):
    return render(request, 'default_route.html')


