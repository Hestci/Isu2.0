from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from myapp import views

urlpatterns = [
    path('lk/', views.lk, name='lk'),
    path('', views.user_login, name='home'),  # Теперь корневой URL ведет на страницу входа
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),  # Оставьте этот маршрут для явного доступа к странице входа
    path('logout/', views.user_logout, name='logout'),  # Новый маршрут
    path('unauthorized/', views.unauthorized, name='unauthorized'),
    path('manage-roles/', views.manage_roles, name='manage_roles'),  # Новый маршрут
]


