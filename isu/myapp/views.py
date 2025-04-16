from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import RegisterForm, LoginForm, ProfileMainForm, ProfileContactForm, ProfileAdditionalForm, ApplicationForm, VacancyForm
from .models import Profile, Role, Application, Vacancy, VacancyResponse
import os
from django.contrib.auth.forms import UserCreationForm

def has_roles(user, role_names=None):
    if not (user.is_authenticated and hasattr(user, 'profile') and user.profile.roles.exists()):
        return False
    if role_names is None:
        return True
    if isinstance(role_names, str):
        role_names = [role_names]
    return user.profile.roles.filter(name__in=role_names).exists()

def is_admin(user):
    print(f"Checking if user {user.username} is admin")
    print(f"Is authenticated: {user.is_authenticated}")
    print(f"Has profile: {hasattr(user, 'profile')}")
    if hasattr(user, 'profile'):
        print(f"Roles: {list(user.profile.roles.all().values_list('name', flat=True))}")
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.roles.filter(name='admin').exists()

@login_required(login_url='/login/')
def home(request):
    if request.user.is_authenticated:
        return redirect('about_university')
    return render(request, 'login.html')

def unauthorized(request):
    return render(request, 'unauthorized.html')

def login_view(request):
    if request.user.is_authenticated:
        if has_roles(request.user):
            return redirect('home')
        else:
            messages.warning(request, 'У вас нет назначенных ролей. Пожалуйста, обратитесь к администратору.')
            return render(request, 'unauthorized.html')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if has_roles(user):
                return redirect('home')
            else:
                messages.warning(request, 'У вас нет назначенных ролей. Пожалуйста, обратитесь к администратору.')
                return render(request, 'unauthorized.html')
        else:
            return render(request, 'login.html', {'form': form, 'error': 'Неверные учетные данные'})
    else:
        form = LoginForm(request)
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='/login/')
def lk(request):
    if not has_roles(request.user):
        messages.warning(request, 'У вас нет назначенных ролей. Пожалуйста, обратитесь к администратору.')
        return render(request, 'unauthorized.html')

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'main_form':
            form = ProfileMainForm(request.POST, instance=request.user.profile)
        elif form_type == 'contact_form':
            form = ProfileContactForm(request.POST, request.FILES, instance=request.user.profile)
        elif form_type == 'additional_form':
            form = ProfileAdditionalForm(request.POST, instance=request.user.profile)
        else:
            form = None

        if form and form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Данные успешно сохранены'
                })
            return redirect('lk')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors if form else {'error': 'Неверный тип формы'}
                })
            return render(request, 'lk.html', {
                'main_form': form if form_type == 'main_form' else ProfileMainForm(instance=request.user.profile),
                'contact_form': form if form_type == 'contact_form' else ProfileContactForm(instance=request.user.profile),
                'additional_form': form if form_type == 'additional_form' else ProfileAdditionalForm(instance=request.user.profile)
            })

    # Создаем формы с начальными данными из модели User
    main_form = ProfileMainForm(instance=request.user.profile)
    contact_form = ProfileContactForm(instance=request.user.profile)
    additional_form = ProfileAdditionalForm(instance=request.user.profile)

    return render(request, 'lk.html', {
        'main_form': main_form,
        'contact_form': contact_form,
        'additional_form': additional_form
    })

def register(request):
    if request.user.is_authenticated:
        if has_roles(request.user):
            return redirect('home')
        else:
            messages.warning(request, 'У вас нет назначенных ролей. Пожалуйста, обратитесь к администратору.')
            return render(request, 'unauthorized.html')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile, created = Profile.objects.get_or_create(user=user)
            
            # Сохраняем данные из формы в профиль
            profile.last_name = form.cleaned_data['last_name']
            profile.first_name = form.cleaned_data['first_name']
            profile.save()
            
            # Сохраняем данные в модель User
            user.last_name = form.cleaned_data['last_name']
            user.first_name = form.cleaned_data['first_name']
            user.save()
            
            # Получаем роль "guest"
            guest_role = Role.objects.get(name='guest')
            # Назначаем роль "guest" пользователю
            profile.roles.add(guest_role)
            
            # Если это первый пользователь, назначаем ему роль admin
            if User.objects.count() == 1:
                admin_role = Role.objects.get(name='admin')
                profile.roles.add(admin_role)
                user.is_staff = True
                user.is_superuser = True
                user.save()
            
            login(request, user)
            return redirect('about_university')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})

@login_required(login_url='/login/')
def admin_panel(request):
    print(f"User: {request.user.username}")
    print(f"Is authenticated: {request.user.is_authenticated}")
    print(f"Has profile: {hasattr(request.user, 'profile')}")
    if hasattr(request.user, 'profile'):
        print(f"Roles: {list(request.user.profile.roles.all().values_list('name', flat=True))}")
    
    if not is_admin(request.user):
        print("User is not admin, redirecting to unauthorized")
        return redirect('unauthorized')
    print("User is admin, rendering admin panel")
    return render(request, 'admin_panel.html')

@login_required(login_url='/login/')
def view_maps(request):
    if not has_roles(request.user):
        messages.warning(request, 'У вас нет назначенных ролей. Пожалуйста, обратитесь к администратору.')
        return render(request, 'unauthorized.html')
    
    # Создаем полные URL для PDF файлов
    pdf_files = ['A.pdf', 'B.pdf', 'Y.pdf']
    pdf_urls = []
    
    for pdf in pdf_files:
        pdf_urls.append({
            'name': pdf,
            'url': f'/static/maps/{pdf}'
        })
    
    return render(request, 'view_maps.html', {'pdf_files': pdf_urls})

@login_required(login_url='/login/')
def about_university(request):
    if not has_roles(request.user):
        messages.warning(request, 'У вас нет назначенных ролей. Пожалуйста, обратитесь к администратору.')
        return render(request, 'unauthorized.html')
    return render(request, 'about_university.html')

@login_required(login_url='/login/')
def manage_roles(request):
    if not is_admin(request.user):
        return redirect('unauthorized')
    
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        role_id = request.POST.get('role_id')
        action = request.POST.get('action')
        
        try:
            profile = Profile.objects.get(user__id=user_id)
            
            if action == 'add':
                role = Role.objects.get(id=role_id)
                profile.roles.add(role)
                messages.success(request, f"Роль {role.name} добавлена пользователю {profile.user.username}.")
            elif action == 'remove':
                role = Role.objects.get(id=role_id)
                profile.roles.remove(role)
                messages.success(request, f"Роль {role.name} удалена у пользователя {profile.user.username}.")
            elif action == 'delete_user':
                return delete_user(request, profile)
            
        except (Profile.DoesNotExist, Role.DoesNotExist):
            messages.error(request, "Пользователь или роль не найдены.")
        return redirect('manage_roles')
    
    users = Profile.objects.all()
    roles = Role.objects.all()
    return render(request, 'manage_roles.html', {
        'users': users,
        'roles': roles
    })

def delete_user(request, profile):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete_user':
            # Проверка на удаление самого себя
            if profile.user == request.user:
                messages.error(request, "Вы не можете удалить свой собственный аккаунт.")
                return redirect('manage_roles')
            
            # Проверка на удаление последнего администратора
            if profile.roles.filter(name='admin').exists():
                admin_count = Profile.objects.filter(roles__name='admin').count()
                if admin_count <= 1:
                    messages.error(request, "Невозможно удалить последнего администратора.")
                    return redirect('manage_roles')
            
            # Удаление пользователя
            username = profile.user.username
            profile.user.delete()
            messages.success(request, f"Пользователь {username} успешно удалён.")
    return redirect('manage_roles')

@login_required(login_url='/login/')
def manage_applications(request):
    if not is_admin(request.user):
        return redirect('unauthorized')
    
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        action = request.POST.get('action')
        
        try:
            application = Application.objects.get(id=application_id)
            if action == 'approve':
                application.status = 'approved'
                # Добавляем роль "student" пользователю
                student_role = Role.objects.get(name='student')
                application.user.profile.roles.add(student_role)
                messages.success(request, f"Заявка от {application.user.username} одобрена.")
            elif action == 'reject':
                application.status = 'rejected'
                messages.success(request, f"Заявка от {application.user.username} отклонена.")
            application.save()
        except Application.DoesNotExist:
            messages.error(request, "Заявка не найдена.")
        return redirect('manage_applications')
    
    applications = Application.objects.all().order_by('-created_at')
    return render(request, 'manage_applications.html', {'applications': applications})

@login_required
def submit_application(request):
    # Проверяем наличие существующей заявки со статусом 'pending'
    if Application.objects.filter(user=request.user, status='pending').exists():
        message = 'У вас уже есть отправленная заявка, которая находится на рассмотрении'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': message})
        else:
            messages.error(request, message)
            return redirect('home')
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            
            # Копируем данные из профиля
            profile = request.user.profile
            application.last_name = profile.last_name
            application.first_name = profile.first_name
            application.middle_name = profile.middle_name
            application.birth_date = profile.birth_date
            application.birth_place = profile.birth_place
            application.document_type = profile.document_type
            application.inn = profile.inn
            application.passport_series = profile.passport_series
            application.passport_number = profile.passport_number
            application.passport_issue_date = profile.passport_issue_date
            application.passport_division_code = profile.passport_division_code
            application.passport_issued_by = profile.passport_issued_by
            
            application.save()
            
            message = 'Заявка успешно отправлена'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': message})
            else:
                messages.success(request, message)
                return redirect('home')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Возвращаем ошибки формы в JSON формате
                errors = {field: form.errors[field][0] for field in form.errors}
                return JsonResponse({
                    'success': False, 
                    'message': 'Ошибка при отправке заявки', 
                    'errors': errors
                })
    else:
        form = ApplicationForm()
    
    return render(request, 'submit_application.html', {'form': form})

@login_required(login_url='/login/')
def vacancies(request):
    vacancies = Vacancy.objects.filter(status='active', is_approved=True)
    
    # Получаем ID вакансий, на которые пользователь уже откликнулся
    user_responses = []
    if request.user.is_authenticated:
        user_responses = VacancyResponse.objects.filter(user=request.user).values_list('vacancy_id', flat=True)
    
    return render(request, 'vacancies.html', {
        'vacancies': vacancies,
        'user_responses': user_responses
    })

@login_required(login_url='/login/')
def create_vacancy(request):
    if not has_roles(request.user, 'Работодатель'):
        return redirect('unauthorized')
    
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.created_by = request.user
            vacancy.save()
            messages.success(request, 'Вакансия успешно создана и ожидает модерации.')
            return redirect('vacancies')
    else:
        form = VacancyForm()
    
    return render(request, 'create_vacancy.html', {'form': form})

@login_required(login_url='/login/')
def manage_vacancies(request):
    if not is_admin(request.user):
        return redirect('unauthorized')
    
    if request.method == 'POST':
        vacancy_id = request.POST.get('vacancy_id')
        action = request.POST.get('action')
        
        try:
            vacancy = Vacancy.objects.get(id=vacancy_id)
            if action == 'approve':
                vacancy.is_approved = True
                vacancy.save()
                messages.success(request, 'Вакансия одобрена.')
            elif action == 'reject':
                vacancy.delete()
                messages.success(request, 'Вакансия отклонена.')
            elif action == 'close':
                vacancy.status = 'closed'
                vacancy.save()
                messages.success(request, 'Вакансия закрыта.')
        except Vacancy.DoesNotExist:
            messages.error(request, 'Вакансия не найдена.')
    
    pending_vacancies = Vacancy.objects.filter(is_approved=False)
    active_vacancies = Vacancy.objects.filter(is_approved=True, status='active')
    return render(request, 'manage_vacancies.html', {
        'pending_vacancies': pending_vacancies,
        'active_vacancies': active_vacancies
    })

@login_required(login_url='/login/')
def my_vacancies(request):
    """Показывает вакансии, созданные текущим пользователем, и отклики на них."""
    # Проверяем, что пользователь имеет роль работодателя
    if not has_roles(request.user, 'Работодатель'):
        messages.error(request, 'У вас нет прав для просмотра этой страницы.')
        return redirect('home')
    
    # Получаем все вакансии пользователя
    vacancies = Vacancy.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Обработка действий с откликами
    if request.method == 'POST':
        response_id = request.POST.get('response_id')
        action = request.POST.get('action')
        
        try:
            response = VacancyResponse.objects.get(id=response_id)
            # Проверяем, что отклик принадлежит вакансии текущего пользователя
            if response.vacancy.created_by != request.user:
                messages.error(request, 'У вас нет прав для выполнения этого действия.')
                return redirect('my_vacancies')
            
            if action == 'accept':
                response.status = 'accepted'
                response.save()
                messages.success(request, f'Отклик от {response.user.username} принят.')
            elif action == 'reject':
                response.status = 'rejected'
                response.save()
                messages.success(request, f'Отклик от {response.user.username} отклонен.')
        except VacancyResponse.DoesNotExist:
            messages.error(request, 'Отклик не найден.')
    
    # Для каждой вакансии получаем все отклики
    vacancy_data = []
    for vacancy in vacancies:
        responses = VacancyResponse.objects.filter(vacancy=vacancy).order_by('-created_at')
        vacancy_data.append({
            'vacancy': vacancy,
            'responses': responses,
            'response_count': responses.count()
        })
    
    return render(request, 'my_vacancies.html', {
        'vacancy_data': vacancy_data,
    })

@login_required(login_url='/login/')
def respond_to_vacancy(request, vacancy_id):
    if request.method == 'POST':
        try:
            vacancy = Vacancy.objects.get(id=vacancy_id, status='active', is_approved=True)
            
            # Проверяем, не является ли пользователь создателем вакансии
            if vacancy.created_by == request.user:
                messages.error(request, 'Вы не можете откликнуться на собственную вакансию.')
                return redirect('vacancies')
            
            # Проверяем, не откликался ли пользователь уже на эту вакансию
            if VacancyResponse.objects.filter(vacancy=vacancy, user=request.user).exists():
                messages.error(request, 'Вы уже откликнулись на эту вакансию.')
                return redirect('vacancies')
            
            message = request.POST.get('message')
            resume = request.FILES.get('resume')
            
            if not message:
                messages.error(request, 'Пожалуйста, напишите сопроводительное письмо.')
                return redirect('vacancies')
            
            # Создаем отклик
            response = VacancyResponse.objects.create(
                vacancy=vacancy,
                user=request.user,
                message=message,
                resume=resume
            )
            
            messages.success(request, f'Ваш отклик на вакансию "{vacancy.title}" успешно отправлен!')
            return redirect('vacancies')
            
        except Vacancy.DoesNotExist:
            messages.error(request, 'Вакансия не найдена или неактивна.')
            return redirect('vacancies')
    
    return redirect('vacancies')

@login_required
def my_responses(request):
    """
    Отображает все отклики текущего пользователя на вакансии с их статусами.
    """
    responses = VacancyResponse.objects.filter(user=request.user).order_by('-created_at')
    
    # Разделение откликов по статусам
    pending_responses = responses.filter(status='pending')
    accepted_responses = responses.filter(status='accepted')
    rejected_responses = responses.filter(status='rejected')
    
    # Общее количество откликов
    total_responses = responses.count()
    
    context = {
        'responses': responses,
        'pending_responses': pending_responses,
        'accepted_responses': accepted_responses,
        'rejected_responses': rejected_responses,
        'total_responses': total_responses
    }
    
    return render(request, 'my_responses.html', context)