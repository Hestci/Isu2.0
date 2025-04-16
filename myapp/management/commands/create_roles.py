from django.core.management.base import BaseCommand
from myapp.models import Role

class Command(BaseCommand):
    help = 'Создание начальных ролей'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начинаю создание ролей...'))
        
        for role_name, display_name in Role.ROLE_CHOICES:
            description = f"Роль {display_name}"
            role, created = Role.objects.get_or_create(
                name=role_name,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана роль: {display_name} ({role_name})'))
            else:
                self.stdout.write(self.style.WARNING(f'Роль {display_name} ({role_name}) уже существует'))
        
        self.stdout.write(self.style.SUCCESS('Процесс создания ролей завершен')) 