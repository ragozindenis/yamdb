![example workflow](https://github.com/ragozindenis/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)


![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

# API для проекта YaMDb

# Проект YaMDb собирает отзывы пользователей на произведения.

## Реализован Action workflow

* автоматический запуск тестов,
* обновление образов на Docker Hub,
* автоматический деплой на боевой сервер при пуше в главную ветку master,
* отправка сообщения в телеграм об успешном прохождении тестов и деплоя.

## Документация API доступна после запуска проекта по адресу:

```
/redoc/
```

## Запуск проекта на удаленном сервере:

### 1. Клонирования репозитария на локальную машину командой:
```
git clone git@github.com:ragozindenis/yamdb_final.git
```
### 2. Далее идем на удаленный сервер:
1. Установка докера:
```
sudo apt install docker.io
```
2. Установка docker-compose:
```
sudo apt-get update
sudo apt-get install docker-compose
```
3. Проверка что все установилось:
```
docker --version
```
```
docker compose version
```
4. Создаем папку на сервере:
```
mkdir nginx
```
5. Копируем файлы docker-compose.yaml и nginx/default.conf с загруженного репозитария на сервер:
```
scp <путь до файла на локальной машине>/<файл> <ваш_username>@<ip/host удаленного сервера>:/home/<ваш_username>/
```
пример:
```
scp /Users/user/Dev/yamdb_final/infra/docker-compose.yaml admin@127.0.0.1:/home/admin/
scp /Users/user/Dev/yamdb_final/infra/nginx/default.conf admin@127.0.0.1:/home/admin/nginx/
```
### 3. Работа с секретами на сайте github:
Перейдите в настройки репозитория Settings, выберите на панели слева Secrets and variables/Actions, нажмите New repository secret и создавайте секреты
```
DB_ENGINE # указываем, что работаем с postgresql - django.db.backends.postgresql
DB_HOST # название сервиса (контейнера)
DB_NAME # имя базы данных
DB_PORT # порт для подключения к БД
POSTGRES_PASSWORD # пароль для подключения к БД (установите свой)
POSTGRES_USER # логин для подключения к базе данных
DOCKER_PASSWORD # логин от Docker Hub
DOCKER_USERNAME # пароль от Docker Hub
HOST # сохраните IP-адрес вашего сервера
PASSPHRASE # пароль для ssh ключа
SECRET_KEY # секретный ключ для файла settings.py
SERVERNAMES # адреса разрешенных серверов через пробел
SSH_KEY # Скопируйте приватный ключ с компьютера, имеющего доступ к серверу командой cat ~/.ssh/id_rsa
TELEGRAM_TO # Узнать свой ID можно у бота @userinfobot
TELEGRAM_TOKEN # Получить этот токен можно у бота @BotFather
USER # имя пользователя для подключения к серверу
```

### 4. Теперь после push'a репозитария с локальной машины запуститься скрипт.

### 5. Идем на сервер для заключительных команд:
> Сделать миграции командами:
```
sudo docker-compose exec web python manage.py makemigrations
```
```
sudo docker-compose exec web python manage.py migrate
```
> Собрать статичные файлы командой:
```
sudo docker-compose exec web python manage.py collectstatic --no-input
```
> Создать суперпользователя командой:
```
sudo docker-compose exec web python manage.py createsuperuser
```
> Админ панель доступна по адресу:
```
/admin/
```
### Проект можно посмотреть по адрессу:
```
51.250.64.236
```
