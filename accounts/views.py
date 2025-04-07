from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import (
    authenticate, 
    login as django_login, 
    logout as django_logout, 
    get_user_model
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages

User = get_user_model() 

def cant_be_authenticated(view):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('home_page'))
        return view(request, *args, **kwargs)
    return wrapper


@cant_be_authenticated
def login(request):
    ctx = {}

    if request.method == "POST":
        username = request.POST.get('username', "").strip()
        password = request.POST.get('password', "").strip()

        if not username or not password:
            messages.error(request, 'Preencha todos os campos, por favor.')
            return redirect(reverse('login'))
        
        user = authenticate(request, username=user, password=password)

        if user is not None:
            django_login(request, user)
            messages.success(request, 'Autenticado com sucesso.')

            return redirect(reverse('home_page'))
        else:
            messages.error(request, 'Username/Password incorrectos.')
            return redirect(reverse('login'))

    return render(request, 'accounts/login.html', ctx)


@cant_be_authenticated
def signup(request):
    ctx = {}

    if request.method == "POST":
        username = request.POST.get('username', "").strip()
        email = request.POST.get('email', "").strip()
        password = request.POST.get('password', "").strip()

        if not username and not email and not password:
            messages.error(request, 'Preencha todos os campos, por favor.')
            return redirect(reverse('signup'))

        if len(password) < 8:
            messages.error(request, 'A palavra-passe é muito fraca.')
            return redirect(reverse('signup'))
        
    return render(request, 'accounts/signup.html', ctx)


@login_required
def logout(request): ...