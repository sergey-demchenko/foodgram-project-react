# Продуктовый помощник  Foodgram

## Описание
Платформа для обмена рецептами


Проект доступен по адресу
Server IP:
[158.160.65.101:8000](http://158.160.65.101:8000/)

### Данные суперпользователя
```
Логин: superuser@gmail.com
Пароль: superusersuperuser
```

### Данные пользователя
```
Логин: user@gmail.com
Пароль: useruser
```

### Данные пользователя 1
```
Логин: user1@gmail.com
Пароль: user1user1
```

### Технологии
- Python
- Django
- Postgres
- Docker

### Как запустить проект на Docker Desktop
Склонируйте проект на свой компьютер:

```
git clone git@github.com:sergey-demchenko/foodgram-project-react.git
```

Создайте и активирйте виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установите зависимости 

```
pip install -r requirements.txt
```

Перейдите в директорию проекта и создайте файл .env:

```
cd infra
```

```
DB_ENGINE=
DB_NAME=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=
DB_PORT=
```

Создайте образ backend:

```
docker build -t sergeydemchenko/foodgram_backend:latest .
```

Перейдите в директорию infra и запустите docker-compose:

```
docker-compose up -d --build
```

Далее выполните миграции создайте суперпользователи и загрузите статические файлы:

```
docker-compose exec web python manage.py migrate
```

```
docker-compose exec web python manage.py createsuperuser
```

```
docker-compose exec web python manage.py collectstatic --no-input
```

Проект будет доступен по адресу:

```
localhost
```



Проект выполнил студент 56 когорты Яндекс Практикума Сергей Демченко
