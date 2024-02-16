from django.contrib import auth
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from .models import RaspberryPi
from .forms import UserRegistrationForm, UserAuthenticationForm
from breadPredictor import BreadPredictor
from django.core.mail import send_mail

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
                user.logged_in = True 
                user.save()
                return redirect('start_process')

    else:
        form = UserAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def start_process(request):
    return render(request, 'start_process.html')

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
        map_user_to_object[raspberry_pi.user] = BreadPredictor(sampleTime = 10)
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
        raspberry_pi = RaspberryPi.objects.get(id=pid)
        user = raspberry_pi.user if raspberry_pi else None
        started = raspberry_pi.start
        logged_in = user.logged_in

    if not logged_in:
        return JsonResponse({'sampling': 10})
    
    print(f'started: {started}')
    if started:
        pred = map_user_to_object[user] 
        pred.sampleTime = float(sampling_time) / 60
        pred.insertData(float(proximity), float(temperature), float(humidity))
         

    return JsonResponse({"sampling": 10})

@csrf_exempt
@login_required
def start(request):
    time = request.POST.get('time')
    yeast = request.POST.get('yeast')
    flour = request.POST.get('flour')
    salt = request.POST.get('salt')
    water = request.POST.get('water')

    print(f'time: {time}, yeast: {yeast}, flour: {flour}, salt: {salt}, water: {water}')

    try:
        raspberry_pi = RaspberryPi.objects.get(user=request.user)
        raspberry_pi.start = True

        if request.user not in map_user_to_object:
            pid_register(request, raspberry_pi.id)
        raspberry_pi.save()

        map_user_to_object[request.user].ingredientTime = float(time)
        map_user_to_object[request.user].yeast = float(yeast)
        map_user_to_object[request.user].flour = float(flour)
        map_user_to_object[request.user].salt = float(salt)
        map_user_to_object[request.user].water = float(water)
        map_user_to_object[request.user].ingredWeight()
        
        return render(request, 'home.html')
    except RaspberryPi.DoesNotExist:
        return render(request, 'error_raspberry.html')

@login_required
def end(request):
    try:
        raspberry_pi = RaspberryPi.objects.get(user=request.user)
        raspberry_pi.start = False
        raspberry_pi.save()
        return render(request, 'home.html')
    except RaspberryPi.DoesNotExist:
        return render(request, 'error_raspberry.html')
    
@login_required
def poll_data(request):
    raspberry_pi = RaspberryPi.objects.get(user=request.user)
    user = raspberry_pi.user 
    started = raspberry_pi.start
    if user in map_user_to_object and started:
        predictor_obj = map_user_to_object[user]
        pred_time = round(predictor_obj.predictTime())
        if pred_time <= 0:
            send_mail(
                'Check your bread!',
                'Check on your bread, the time is up! 🍞',
                'icldough@gmail.com',
                [user.email],
                fail_silently=False,
            )
            raspberry_pi.start = False
            raspberry_pi.save()

            return JsonResponse({'temp': '---', 'humid': '---', 'tof': '---', 'pred': 0})

        if len(predictor_obj.height) > 0 and  len(predictor_obj.temp)> 0 and len(predictor_obj.humid) > 0:
            tof, temp, humid = predictor_obj.height[-1], predictor_obj.temp[-1], predictor_obj.humid[-1]
            return JsonResponse({'temp': round(temp, 2), 'humid': round(humid, 2), 'bread_height': round(tof), 'pred': round(predictor_obj.predictTime())})
        else:
            return JsonResponse({'temp': '---', 'humid': '---', 'tof': '---', 'pred': '---'})
    return JsonResponse({'temp': '---', 'humid': '---', 'tof': '---', 'pred': '---'})

def logout(request):
    user = request.user
    user.logged_in = False  
    user.save()
    auth.logout(request)
    return redirect('default_route')
   
def default_route(request):
    return render(request, 'default_route.html')







