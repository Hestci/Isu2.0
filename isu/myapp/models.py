from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)

    # Основная информация
    last_name = models.CharField(max_length=100, verbose_name='Фамилия', blank=True)
    first_name = models.CharField(max_length=100, verbose_name='Имя', blank=True)
    middle_name = models.CharField(max_length=100, verbose_name='Отчество', blank=True, null=True)
    birth_place = models.CharField(max_length=200, verbose_name='Место рождения', default='Не указано')

    # Паспортные данные
    document_type = models.CharField(max_length=20, choices=[
        ('passport', 'Паспорт'),
        ('foreign_passport', 'Заграничный паспорт')
    ], default='passport', verbose_name='Тип документа')
    inn = models.CharField(max_length=12, verbose_name='ИНН', blank=True, null=True)
    passport_series = models.CharField(max_length=4, verbose_name='Серия паспорта', default='0000')
    passport_number = models.CharField(max_length=6, verbose_name='Номер паспорта', default='000000')
    passport_issue_date = models.DateField(verbose_name='Дата выдачи', default='2000-01-01')
    passport_division_code = models.CharField(max_length=7, verbose_name='Код подразделения', default='000-000')
    passport_issued_by = models.CharField(max_length=200, verbose_name='Кем выдан', default='Не указано')

    # Дополнительная информация
    education = models.TextField(verbose_name='Образование', blank=True, null=True)
    resume = models.TextField(verbose_name='Резюме', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def has_role(self, role_name):
        return self.roles.filter(name=role_name).exists()

    def is_admin(self):
        return self.has_role('admin')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        # Синхронизируем данные между User и Profile
        instance.profile.last_name = instance.last_name
        instance.profile.first_name = instance.first_name
        instance.profile.save()

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    document = models.FileField(upload_to='applications/', verbose_name='Документ')
    
    # Копия данных из профиля на момент подачи заявки
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    middle_name = models.CharField(max_length=100, verbose_name='Отчество', blank=True, null=True)
    birth_date = models.DateField(verbose_name='Дата рождения')
    birth_place = models.CharField(max_length=200, verbose_name='Место рождения')
    document_type = models.CharField(max_length=20, choices=[
        ('passport', 'Паспорт'),
        ('foreign_passport', 'Заграничный паспорт')
    ], verbose_name='Тип документа')
    inn = models.CharField(max_length=12, verbose_name='ИНН', blank=True, null=True)
    passport_series = models.CharField(max_length=4, verbose_name='Серия паспорта')
    passport_number = models.CharField(max_length=6, verbose_name='Номер паспорта')
    passport_issue_date = models.DateField(verbose_name='Дата выдачи')
    passport_division_code = models.CharField(max_length=7, verbose_name='Код подразделения')
    passport_issued_by = models.CharField(max_length=200, verbose_name='Кем выдан')

    def __str__(self):
        return f"Заявка от {self.user.username} ({self.created_at.strftime('%d.%m.%Y')})"

class Vacancy(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('closed', 'Закрыта'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название вакансии')
    company = models.CharField(max_length=200, verbose_name='Компания')
    description = models.TextField(verbose_name='Описание')
    requirements = models.TextField(verbose_name='Требования')
    salary = models.CharField(max_length=100, verbose_name='Зарплата', blank=True)
    location = models.CharField(max_length=200, verbose_name='Местоположение')
    contact_info = models.TextField(verbose_name='Контактная информация')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacancies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.company}"

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-created_at']

class VacancyResponse(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено')
    ]
    
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='responses', verbose_name='Вакансия')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacancy_responses', verbose_name='Пользователь')
    message = models.TextField(verbose_name='Сопроводительное письмо')
    resume = models.FileField(upload_to='vacancy_responses/', verbose_name='Резюме', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отклика')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')

    def __str__(self):
        return f"Отклик от {self.user.username} на вакансию {self.vacancy.title}"

    class Meta:
        verbose_name = 'Отклик на вакансию'
        verbose_name_plural = 'Отклики на вакансии'
        ordering = ['-created_at']
        # Один пользователь может оставить только один отклик на конкретную вакансию
        unique_together = ('vacancy', 'user')