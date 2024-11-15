# Описание

Фудграм — сервис, на котором пользователи публикуют рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

# Стек:
python, docker, postgreSQL, nginx, gunicorn, django, DRF, djoser, JSON, YAML, postman.

# Данные для подключения
Адрес: https://foodgram-ilya.ddns.net


# Как запустить проект
Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:chvyarepaxa/foodgram-project-react.git
```

```
cd foodgram-project-react
```

Запустите Docker Compose:

```
sudo docker compose -f docker-compose.production.yml up -d
```

Соберите и переложите статику бэкенда:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

```
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
```

Выполните миграции:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

Создайте суперпользователя:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

Настройте обратный прокси-сервер на перенаправление запросов в докер.
В случае использования Nginx, часть файла конфигурации, ответственная за перенаправление может выглядеть так:

```
nano /etc/nginx/sites-enabled/default
```

```
 location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000;
    }
```

Проверьте корректность конфигурации обратного прокси-сервера.
В случае использования Nginx:

```
sudo nginx -t
```

Перезагрузите обратный прокси-сервер.
В случаи использования Nginx:

```
sudo service nginx reload
```

# API
В проекте реализован API.

Для просмотра спецификации перейдите из корневой директории проекта в папку infra

```
cd infra
```

Выполните команду docker-compose up:

```
sudo docker-compose up
```

Спецификация API будет доступна по адресу http://localhost/api/docs/
