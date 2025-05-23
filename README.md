# ISU 2.0

Веб-приложение для управления пользователями, ролями и вакансиями в университетской системе.

## Функциональность

- Регистрация и авторизация пользователей
- Управление ролями пользователей (администратор, гость, студент, работодатель)
- Личный кабинет пользователя
- Административная панель
- Просмотр карт и информации об университете
- Подача заявок на обучение
- Управление заявками на обучение
- Размещение и управление вакансиями
- Модерация вакансий администраторами
- Просмотр детальной информации о заявках
- Обновление статусов заявок с автоматическим назначением ролей

## Технологии

- Python 3.11
- Django 5.2
- PostgreSQL
- Docker
- Bootstrap 5
- jQuery

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Hestci/isu2.0.git
cd isu2.0
```

2. Запустите приложение с помощью Docker Compose:
```bash
docker compose up --build -d
```
3. Создайте начальные роли:
```bash
docker compose exec web python manage.py create_initial_roles
```

Результат выполнения команды:
```bash
Successfully created role admin
Successfully created role student
Successfully created role Работодатель
Successfully created role teacher
Successfully created role guest
```

4. Создайте необходимые директории для хранения файлов:
```bash
docker compose exec web mkdir -p media/applications
docker compose exec web chmod 777 media/applications
```
5. Примените миграции для создания таблиц в базе данных:
```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

6. Копирование PDF-файлов для просмотра карт:

```bash
# Узнаем имя web-контейнера
docker compose ps
# Результат будет примерно таким: isu20-web-1 или project_name-web-1
```

Способ 1 (если у вас есть готовые PDF-файлы):
```bash
# Создаем временную директорию в контейнере
docker compose exec web mkdir -p /tmp/maps

# Копируем PDF-файлы во временную директорию (замените isu20-web-1 на имя вашего контейнера)
docker cp isu/myapp/static/maps/A.pdf isu20-web-1:/tmp/maps/
docker cp isu/myapp/static/maps/B.pdf isu20-web-1:/tmp/maps/
docker cp isu/myapp/static/maps/Y.pdf isu20-web-1:/tmp/maps/

# Создаем директории для статических файлов
docker compose exec web mkdir -p /app/myapp/static/maps
docker compose exec web mkdir -p /app/staticfiles/maps

# Копируем файлы в директории статических файлов
docker compose exec web cp /tmp/maps/A.pdf /app/myapp/static/maps/
docker compose exec web cp /tmp/maps/B.pdf /app/myapp/static/maps/
docker compose exec web cp /tmp/maps/Y.pdf /app/myapp/static/maps/
docker compose exec web cp /tmp/maps/A.pdf /app/staticfiles/maps/
docker compose exec web cp /tmp/maps/B.pdf /app/staticfiles/maps/
docker compose exec web cp /tmp/maps/Y.pdf /app/staticfiles/maps/
```

Способ 2 (создание тестовых PDF-файлов прямо в контейнере):
```bash
# Создаем директории для статических файлов
docker compose exec web mkdir -p /app/myapp/static/maps
docker compose exec web mkdir -p /app/staticfiles/maps

# Создаем минимальные тестовые PDF-файлы
docker compose exec web bash -c "echo '%PDF-1.4' > /app/myapp/static/maps/A.pdf"
docker compose exec web bash -c "echo '%PDF-1.4' > /app/myapp/static/maps/B.pdf"
docker compose exec web bash -c "echo '%PDF-1.4' > /app/myapp/static/maps/Y.pdf"
docker compose exec web bash -c "echo '%PDF-1.4' > /app/staticfiles/maps/A.pdf"
docker compose exec web bash -c "echo '%PDF-1.4' > /app/staticfiles/maps/B.pdf"
docker compose exec web bash -c "echo '%PDF-1.4' > /app/staticfiles/maps/Y.pdf"
```

# Запускаем сбор статических файлов и перезапускаем сервер
```bash
docker compose exec web python manage.py collectstatic --noinput
docker compose restart web
```

## Структура проекта

```
isu2.0/
├── isu/                    # Основной проект Django
│   ├── myapp/             # Приложение
│   │   ├── migrations/    # Миграции базы данных
│   │   ├── templates/     # HTML шаблоны
│   │   │   ├── admin/     # Шаблоны для админ-панели
│   │   │   ├── auth/      # Шаблоны для авторизации
│   │   ├── static/        # Статические файлы
│   │   ├── models.py      # Модели данных
│   │   ├── views.py       # Представления
│   │   └── urls.py        # URL-маршруты
│   ├── settings.py        # Настройки проекта
│   └── urls.py            # Корневые URL-маршруты
├── docker-compose.yml     # Конфигурация Docker Compose
├── Dockerfile            # Конфигурация Docker
└── requirements.txt      # Зависимости Python
```

## Роли пользователей

- **Администратор (admin)**: полный доступ ко всем функциям системы
- **Гость (guest)**: базовый доступ к просмотру информации
- **Студент (student)**: доступ к учебным материалам и функциям
- **Работодатель (Работодатель)**: возможность размещать и управлять вакансиями
- **Преподаватель (teacher)**

## Система аутентификации

1. Вход в систему:
   - Страница входа доступна по адресу `/login/`
   - Поддержка восстановления пароля через email
   - Перенаправление авторизованных пользователей на домашнюю страницу

2. Управление доступом:
   - Ролевая система прав доступа
   - Проверка наличия ролей через функцию `has_role`
   - Защита административных маршрутов через декораторы

## Административная панель

1. Управление пользователями:
   - Просмотр списка пользователей
   - Назначение и управление ролями через интерфейс
   - Блокировка/разблокировка аккаунтов

2. Управление заявками:
   - Просмотр всех поданных заявок
   - Сортировка по статусам: на рассмотрении, принятые, отклоненные
   - Скачивание прикрепленных документов
   - Изменение статуса заявок с автоматическим назначением роли "студент"
   - Детальный просмотр информации о заявке

3. Управление вакансиями:
   - Модерация размещенных вакансий
   - Возможность блокировки неприемлемых вакансий
   - Статистика по размещенным вакансиям

## Функции заявок на обучение

1. Подача заявки:
   - Доступна пользователям без ролей
   - Требуется загрузка PDF-документа
   - Автоматическое копирование данных из профиля
   - Защита от двойной отправки формы

2. Управление заявками:
   - Просмотр списка всех заявок
   - Детальная информация о каждой заявке
   - Скачивание прикрепленных документов
   - Одобрение/отклонение заявок
   - Автоматическое назначение роли "студент" при одобрении

3. Мои заявки:
   - Просмотр собственных заявок пользователем
   - Категоризация по статусам: на рассмотрении, принятые, отклоненные

## Функции вакансий

1. Размещение вакансий:
   - Доступно пользователям с ролью "Работодатель"
   - Требуется заполнение полной информации о вакансии
   - Автоматическая отправка на модерацию

2. Управление вакансиями:
   - Просмотр списка всех вакансий
   - Одобрение/отклонение вакансий администраторами
   - Возможность закрытия вакансий
   - Детальный просмотр информации о вакансии

## Личный кабинет

1. Профиль пользователя:
   - Обновление личной информации
   - Загрузка и обновление аватара
   - Просмотр назначенных ролей

2. Отклики на вакансии:
   - Просмотр статусов собственных откликов
   - Сортировка по статусам: на рассмотрении, принятые, отклоненные

## URL-маршруты

- `/login/` - страница входа
- `/logout/` - выход из системы
- `/` - главная страница (перенаправляет на вход)
- `/home/` - домашняя страница после авторизации
- `/lk/` - личный кабинет пользователя
- `/admin-panel/` или `/my-admin/` - административная панель
- `/manage-roles/` или `/my-admin/users/` - управление ролями пользователей
- `/manage-applications/` или `/my-admin/applications/` - управление заявками
- `/manage-vacancies/` или `/my-admin/vacancies/` - управление вакансиями
- `/submit-application/` - подача заявки на обучение
- `/vacancies/` - просмотр всех вакансий
- `/my-vacancies/` - мои вакансии (для работодателей)
- `/my-responses/` - мои отклики на вакансии
- `/view-maps/` - просмотр карт университета
- `/about-university/` - информация об университете

## Дополнительная информация

Проект использует Docker для создания изолированной среды разработки и запуска, что обеспечивает единообразие работы на разных платформах. Вся бизнес-логика реализована с использованием Django, а для пользовательского интерфейса применяется Bootstrap 5 с некоторыми кастомными стилями.

