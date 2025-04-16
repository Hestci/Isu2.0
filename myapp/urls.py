from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    # Admin panel URLs
    path('admin/applications/', views.manage_applications, name='manage_applications'),
    path('admin/vacancies/', views.manage_vacancies, name='manage_vacancies'),
    path('admin/roles/', views.manage_roles, name='manage_roles'),

    # Application URLs
    path('applications/submit/', views.submit_application, name='submit_application'),

    # Home page
    path('home/', views.home, name='home'),
    
    # Main URLs
    path('lk/', views.lk, name='lk'),
    
    # Other URLs
    path('view-maps/', views.view_maps, name='view_maps'),
    path('about-university/', views.about_university, name='about_university'),
    path('unauthorized/', views.unauthorized, name='unauthorized'),
] 