from django.db import models
from django.contrib.auth.models import AbstractUser, Group

class User(AbstractUser):
    roles = models.ManyToManyField('Role', related_name='users')
    
    def __str__(self):
        return self.username
        
    def has_role(self, role_name):
        if hasattr(self, 'profile'):
            return self.profile.roles.filter(name=role_name).exists()
        return False

class Role(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('student', 'Студент'),
        ('Работодатель', 'Работодатель'),
    ]
    
    name = models.CharField(max_length=20, unique=True, choices=ROLE_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_name_display()

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    @classmethod
    def create_default_roles(cls):
        for role_name, display_name in cls.ROLE_CHOICES:
            description = f"Роль {display_name}"
            cls.objects.get_or_create(
                name=role_name,
                defaults={'description': description}
            )

class VacancyResponse(models.Model):
    vacancy = models.ForeignKey('Vacancy', on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    resume = models.FileField(upload_to='vacancy_responses/')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'На рассмотрении'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено')
    ], default='pending')

    class Meta:
        verbose_name = 'Отклик на вакансию'
        verbose_name_plural = 'Отклики на вакансии'

    def __str__(self):
        return f'Отклик от {self.user.username} на вакансию {self.vacancy.title}' 