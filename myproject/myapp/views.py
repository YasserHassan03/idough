from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from .models import RaspberryPi
from .forms import UserRegistrationForm, UserAuthenticationForm
import subprocess
import breadPredictor

map_user_to_object = {}

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
    user_raspberries = RaspberryPi.objects.filter(user=request.user)

    context = {
        'temp': "---",
        'humid': "---",
        'tof': "---",
        'sampling': "---",
        'user_raspberries': user_raspberries
    }
    
    return render(request, 'home.html')

@login_required
def register_raspberry(request):
    if request.method == 'POST':
        raspberry_id = request.POST.get('raspberry_id')
        raspberry = RaspberryPi.objects.filter(id=raspberry_id).first()
        if not raspberry:
            return render(request, 'registration/register_raspberry.html', {'error': 'Invalid Raspberry Pi ID'})
        if raspberry.user:
            return render(request, 'registration/register_raspberry.html', {'error': 'Raspberry Pi already registered'})
        raspberry.user = request.user
        raspberry.save()
        return redirect('home')
    else:
        return render(request, 'registration/register_raspberry.html')

def pid_register(request, raspberry_id):
    try:
        raspberry_pi = RaspberryPi.objects.get(id=raspberry_id)
        if raspberry_pi.user is None:
            return HttpResponseForbidden({'error': 'Raspberry Pi user not found'})
        map_user_to_object[raspberry_pi.user] = breadPredictor.breadPredictor()
        return JsonResponse({'success': "Raspberry Pi user found"})
    
    except RaspberryPi.DoesNotExist:
        return HttpResponseForbidden({'error': 'Raspberry Pi not found'})
   
@csrf_exempt
def sensors(request):
    if request.method == 'POST':
        temperature = request.POST.get('temp')
        humidity = request.POST.get('humid')
        proximity = request.POST.get('tof')
        sampling_time = request.POST.get('sampling')
        pid = request.POST.get('pid')
        print(f'pId: {pid}, type: {type(pid)}')
        raspberry_pi = RaspberryPi.objects.get(id=pid)
        # user_raspberries = RaspberryPi.objects.filter(user=request.user)
        
        user = raspberry_pi.user if raspberry_pi else None


    context = {
        'temp': temperature,
        'humid': humidity,
        'tof': proximity,
        'sampling': sampling_time,
        'user_raspberries': user
    }
   
     

    # print(f'ctx: {context}')
   
    return JsonResponse({"sampling": sampling_time})


    # render(request, "home.html", context)

def default_route(request):
    return render(request, 'default_route.html')



