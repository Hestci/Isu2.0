from django.db import migrations

def create_roles(apps, schema_editor):
    Role = apps.get_model('myapp', 'Role')
    default_roles = {
        'admin': 'Полный доступ ко всем функциям системы',
        'guest': 'Базовый доступ к просмотру информации',
        'student': 'Доступ к учебным материалам и функциям',
        'Работодатель': 'Возможность размещать и управлять вакансиями',
        'user_manager': 'Управление пользователями и их ролями',
        'application_manager': 'Управление заявками на обучение',
        'vacancy_manager': 'Управление вакансиями и их модерацией'
    }
    
    for role_name, description in default_roles.items():
        Role.objects.get_or_create(
            name=role_name,
            defaults={'description': description}
        )

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_roles),
    ] 