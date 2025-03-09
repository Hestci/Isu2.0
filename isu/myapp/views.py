from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("home")
        else:
            messages.error(request, "Ошибка в данных формы.")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('lk')
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Вы успешно вошли!")
                return redirect('lk')
            else:
                messages.error(request, "Неверное имя пользователя или пароль.")
        else:
            messages.error(request, "Ошибка в данных формы.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})

@login_required(login_url='/unauthorized/')
def lk(request):
    return render(request, 'lk.html', {'user': request.user})

def user_logout(request):
    logout(request)
    messages.success(request, "Вы успешно вышли из аккаунта.")
    return redirect('login')

def unauthorized(request):
    return render(request, 'unauthorized.html')