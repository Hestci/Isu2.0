import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Команда для ожидания готовности базы данных"""

    def handle(self, *args, **options):
        self.stdout.write('Ожидание базы данных...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('База данных недоступна, ожидание 1 секунду...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('База данных доступна!')) 