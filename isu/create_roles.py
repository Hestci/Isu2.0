import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isu.settings')
django.setup()

from myapp.models import Role

def create_roles():
    print("Начинаю создание ролей...")
    for role_name, display_name in Role.ROLE_CHOICES:
        description = f"Роль {display_name}"
        role, created = Role.objects.get_or_create(
            name=role_name,
            defaults={'description': description}
        )
        if created:
            print(f"Создана роль: {display_name} ({role_name})")
        else:
            print(f"Роль {display_name} ({role_name}) уже существует")
    print("Процесс создания ролей завершен")

if __name__ == "__main__":
    create_roles() 