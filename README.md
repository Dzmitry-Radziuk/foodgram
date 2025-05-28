# Foodgram 🥘
REST API для публикации и управления рецептами с авторизацией, избранным, подписками и генерацией списка покупок.

![CI](https://github.com/Dzmitry-Radziuk/foodgram/actions/workflows/main.yml/badge.svg)

Foodgram — это REST API сервис для управления рецептами, пользователями, избранным и подписками. Проект выполнен на Django REST Framework и контейнеризован с помощью Docker.

## ⚙️ Функциональность

- 👤 Регистрация и аутентификация пользователей  
- 📜 CRUD для рецептов с тегами и ингредиентами  
- 🖼 Загрузка изображений рецептов (base64)  
- ⭐ Добавление/удаление рецептов в избранное  
- 🔔 Подписка/отписка на авторов рецептов  
- 🛒 Генерация списка покупок (список ингредиентов)  

## 🛠 Технологии

- 🐍 Python 3.12  
- 🌐 Django & Django REST Framework  
- 🔐 Djoser (аутентификация)  
- 🐘 PostgreSQL  
- 🐳 Docker & Docker Compose  
- 🌍 Nginx  
- ⚙️ GitHub Actions (CI/CD)  


## 🚀 Установка и запуск с Docker

Клонируйте репозиторий и перейдите в папку проекта:
```bash
git clone https://github.com/Dzmitry-Radziuk/foodgram.git
cd foodgram
```
Создайте файл .env по шаблону:
```bash
SECRET_KEY=<ваш_секрет>
DEBUG=False
ALLOWED_HOSTS=<ваш_домен>
POSTGRES_DB=<имя_бд>
POSTGRES_USER=<пользователь_бд>
POSTGRES_PASSWORD=<пароль_бд>
DB_HOST=db
DB_PORT=5432
```
Запуск сборки и поднятие контейнеров:
```bash
docker compose -f docker-compose.yml up -d --build
```
Для автоматического применения миграций, сбора статики и наполнения базы данных ингредиентами и тегами используется скрипт backend/entrypoint.sh.
Если по каким-то причинам необходимо выполнить эти шаги вручную, можно выполнить следующие команды:
```bash
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients
docker compose -f docker-compose.production.yml exec backend python manage.py load_tags
```
Перейдите на https://<ваш_домен> — приложение доступно!

## 💻 Локальный запуск без Docker

Установите зависимости Python:
```bash
cd backend/
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```
Установите зависимости фронтенда:
```bash
cd ../frontend/
npm ci
```
Настройте .env, мигрируйте БД и запустите проект:
```bash
cd ../backend/
python manage.py migrate
python manage.py runserver
```
API будет доступен по адресу http://127.0.0.1:8000/api/.


## 🔄 CI/CD

- Автоматический запуск тестов
- Сборка и публикация Docker-образов
- Деплой на сервер через SSH и Docker Compose

## ✅ Тестирование

Для запуска тестов используйте:
```bash
pytest backend/tests/
```
```md
## 📡 Примеры API эндпоинтов

Ниже приведены основные пути для работы с REST API:

| Метод | Путь                                  | Описание                                   |
|-------|---------------------------------------|--------------------------------------------|
| POST  | `/api/users/`                         | Регистрация нового пользователя            |
| POST  | `/api/auth/token/`                    | Получение токена (логин + пароль)          |
| GET   | `/api/users/me/`                      | Получение данных текущего пользователя     |
| GET   | `/api/recipes/`                       | Список всех рецептов                       |
| POST  | `/api/recipes/`                       | Создание нового рецепта (токен в заголовке)|
| GET   | `/api/recipes/{id}/`                  | Подробности конкретного рецепта            |
| POST  | `/api/recipes/{id}/favorite/`         | Добавить рецепт в избранное                |
| DELETE| `/api/recipes/{id}/favorite/`         | Удалить рецепт из избранного               |
| POST  | `/api/recipes/{id}/shopping_cart/`    | Добавить рецепт в список покупок           |
| DELETE| `/api/recipes/{id}/shopping_cart/`    | Удалить рецепт из списка покупок           |
| GET   | `/api/ingredients/?name=сахар`        | Поиск ингредиентов по названию             |
| POST  | `/api/users/{id}/subscribe/`          | Подписаться на автора                      |
| DELETE| `/api/users/{id}/subscribe/`          | Отписаться от автора                       |
| GET   | `/api/subscriptions/`                 | Список текущих подписок                    |


## 📚 Документация API

 - ReDoc: [Открыть документацию](https://foodgram.webhop.me/api/docs)
 - Сайт: [Открыть сайт проекта](https://foodgram.webhop.me)

## 👨‍💻 Автор

Дмитрий Радюк — Python-разработчик GitHub: [Dzmitry Radziuk](https://github.com/Dzmitry-Radziuk)
