import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isu.settings')
django.setup()

from myapp.models import Role

# Создаем роль "Работодатель"
role, created = Role.objects.get_or_create(
    name='Работодатель',
    defaults={
        'description': 'Роль для размещения вакансий'
    }
)

if created:
    print(f'Роль "{role.name}" успешно создана')
else:
    print(f'Роль "{role.name}" уже существует') 