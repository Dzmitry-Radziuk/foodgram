#!/bin/sh
set -e

echo "Ожидаем подключения к базе данных на $POSTGRES_HOST:$POSTGRES_PORT..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "База данных недоступна, ждем..."
  sleep 1
done

echo "База данных доступна, выполняем миграции и собираем статику"
python manage.py migrate &&
python manage.py collectstatic --noinput &&
python manage.py load_ingredients &&
python manage.py load_tags
exec gunicorn backend.wsgi:application --bind 0.0.0.0:8000