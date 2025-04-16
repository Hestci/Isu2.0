from django.core.management.base import BaseCommand
from myapp.models import Role

class Command(BaseCommand):
    help = 'Creates initial roles in the database'

    def handle(self, *args, **options):
        roles = [
            ('admin', 'Администратор системы'),
            ('student', 'Студент'),
            ('Работодатель', 'Работодатель'),
            ('teacher', 'Преподаватель'),
            ('guest', 'Гость')
        ]
        
        for role_name, description in roles:
            Role.objects.get_or_create(
                name=role_name,
                defaults={'description': description}
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created role {role_name}')) 