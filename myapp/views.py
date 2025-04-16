from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import User, Role, Application, Vacancy, VacancyResponse
from .forms import ApplicationForm, VacancyForm

def has_admin_role(user):
    if not user.is_authenticated:
        return False
    return any(user.has_role(role) for role in ['admin', 'user_manager', 'application_manager', 'vacancy_manager'])

@login_required
@user_passes_test(has_admin_role)
def admin_panel(request):
    return render(request, 'admin_panel.html')

@login_required
@user_passes_test(lambda u: u.has_role('user_manager') or u.has_role('admin'))
def manage_roles(request):
    users = User.objects.all()
    roles = Role.objects.all()
    return render(request, 'admin/manage_roles.html', {'users': users, 'roles': roles})

@login_required
@user_passes_test(lambda u: u.has_role('application_manager') or u.has_role('admin'))
def manage_applications(request):
    applications = Application.objects.all()
    return render(request, 'admin/manage_applications.html', {'applications': applications})

@login_required
@user_passes_test(lambda u: u.has_role('vacancy_manager') or u.has_role('admin'))
def manage_vacancies(request):
    vacancies = Vacancy.objects.all()
    return render(request, 'admin/manage_vacancies.html', {'vacancies': vacancies})

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def vacancy_list(request):
    vacancies = Vacancy.objects.filter(status='active')
    return render(request, 'vacancies/vacancy_list.html', {'vacancies': vacancies})

@login_required
def respond_to_vacancy(request, vacancy_id):
    if request.method == 'POST':
        vacancy = Vacancy.objects.get(id=vacancy_id)
        message = request.POST.get('message')
        resume = request.FILES.get('resume')
        
        if not message or not resume:
            messages.error(request, 'Пожалуйста, заполните все поля')
            return redirect('vacancy_list')
        
        response = VacancyResponse.objects.create(
            vacancy=vacancy,
            user=request.user,
            message=message,
            resume=resume
        )
        
        messages.success(request, 'Ваш отклик успешно отправлен')
        return redirect('vacancy_list')
    
    return redirect('vacancy_list')

@login_required
@user_passes_test(lambda u: u.has_role('user_manager') or u.has_role('admin'))
def update_user_roles(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    all_roles = Role.objects.all()
    
    if request.method == 'POST':
        # Remove all existing roles
        if hasattr(target_user, 'profile'):
            target_user.profile.roles.clear()
            
            # Add selected roles
            role_ids = request.POST.getlist('roles')
            selected_roles = Role.objects.filter(id__in=role_ids)
            target_user.profile.roles.add(*selected_roles)
            
            messages.success(request, f'Роли пользователя {target_user.username} обновлены')
        else:
            messages.error(request, 'У пользователя отсутствует профиль')
        
        return redirect('manage_roles')
    
    # For GET request, show form with current roles
    context = {
        'target_user': target_user,
        'all_roles': all_roles,
        'user_roles': target_user.profile.roles.all() if hasattr(target_user, 'profile') else []
    }
    
    return render(request, 'admin/update_user_roles.html', context)

@login_required
@user_passes_test(lambda u: u.has_role('application_manager') or u.has_role('admin'))
def view_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    return render(request, 'admin/view_application.html', {'application': application})

@login_required
@user_passes_test(lambda u: u.has_role('application_manager') or u.has_role('admin'))
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in [s[0] for s in Application.STATUS_CHOICES]:
            application.status = status
            application.save()
            
            # If the application is approved, add the student role to the user
            if status == 'approved':
                student_role = Role.objects.get(name='student')
                if hasattr(application.user, 'profile'):
                    application.user.profile.roles.add(student_role)
                    messages.success(request, f'Заявка {application_id} одобрена. Пользователю {application.user.username} добавлена роль "Студент".')
                else:
                    messages.warning(request, f'Заявка {application_id} одобрена, но у пользователя отсутствует профиль для добавления роли.')
            else:
                messages.success(request, f'Статус заявки {application_id} изменен на "{dict(Application.STATUS_CHOICES)[status]}".')
        else:
            messages.error(request, 'Некорректный статус заявки.')
            
    return redirect('manage_applications')

# ... existing code ... 