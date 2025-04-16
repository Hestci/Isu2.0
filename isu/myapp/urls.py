from django.contrib import admin
from django.urls import path
from . import views
from .views import submit_application
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('lk/', views.lk, name='lk'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('my-admin/dashboard/', views.admin_panel, name='admin_dashboard'),
    path('manage-roles/', views.manage_roles, name='manage_roles'),
    path('manage-applications/', views.manage_applications, name='manage_applications'),
    path('submit-application/', submit_application, name='submit_application'),
    path('view-maps/', views.view_maps, name='view_maps'),
    path('about-university/', views.about_university, name='about_university'),
    path('unauthorized/', views.unauthorized, name='unauthorized'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('create-vacancy/', views.create_vacancy, name='create_vacancy'),
    path('manage-vacancies/', views.manage_vacancies, name='manage_vacancies'),
    path('my-vacancies/', views.my_vacancies, name='my_vacancies'),
    path('my-responses/', views.my_responses, name='my_responses'),
    path('respond-to-vacancy/<int:vacancy_id>/', views.respond_to_vacancy, name='respond_to_vacancy'),
    path('accounts/login/', LoginView.as_view(template_name='login.html'), name='django_login'),
    path('password_reset/', PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('my-admin/', views.admin_panel, name='admin_panel'),
    path('my-admin/users/', views.manage_roles, name='manage_roles'),
    path('my-admin/applications/', views.manage_applications, name='manage_applications'),
    path('my-admin/vacancies/', views.manage_vacancies, name='manage_vacancies'),
    # Temporarily remove these paths until we resolve the view function issue
    # path('my-admin/update-roles/<int:user_id>/', views.update_user_roles, name='update_user_roles'),
    # path('view-application/<int:application_id>/', views.view_application, name='view_application'),
    # path('update-application-status/<int:application_id>/', views.update_application_status, name='update_application_status'),
]


