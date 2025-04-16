import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isu.settings')
django.setup()

from myapp.models import Role

def check_roles():
    print("Existing roles:")
    for role in Role.objects.all():
        print(f"- {role.name}: {role.description}")

if __name__ == '__main__':
    check_roles() 