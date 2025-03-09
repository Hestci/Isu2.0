from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User  # Добавляем импорт User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from .models import Profile  # Убеждаемся, что Profile импортирован

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаём профиль для пользователя
            if User.objects.count() == 1:  # Если это первый пользователь
                Profile.objects.create(user=user, role='admin')
            else:
                Profile.objects.create(user=user, role='student')  # По умолчанию студент
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("home")
        else:
            messages.error(request, "Ошибка в данных формы.")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

# Остальные функции остаются без изменений пока
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

@login_required(login_url='/unauthorized/')
def manage_roles(request):
    if request.user.profile.role != 'admin':  # Только админ может менять роли
        messages.error(request, "У вас нет прав для управления ролями.")
        return redirect('lk')
    
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        try:
            profile = Profile.objects.get(user__id=user_id)
            if new_role in ['student', 'teacher', 'admin']:
                profile.role = new_role
                profile.save()
                messages.success(request, f"Роль пользователя {profile.user.username} изменена на {new_role}.")
            else:
                messages.error(request, "Недопустимая роль.")
        except Profile.DoesNotExist:
            messages.error(request, "Пользователь не найден.")
        return redirect('manage_roles')
    
    users = Profile.objects.all()  # Список всех пользователей
    return render(request, 'manage_roles.html', {'users': users})