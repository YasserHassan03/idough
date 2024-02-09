from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserAuthenticationForm

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

    context = {
        'temperature': temperature,
        'proximity': proximity,
        'current_time': current_time,
    }
    
    return render(request, 'home.html', context)


def default_route(request):
    return render(request, 'default_route.html')


