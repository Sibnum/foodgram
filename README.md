# Foodgram – продуктовый помощник

![GitHub Actions Workflow Status](https://github.com/Sibnum/foodgram/actions/workflows/main.yml/badge.svg)

Репозиторий проекта: [https://github.com/Sibnum/foodgram.git](https://github.com/Sibnum/foodgram.git)

Имя ресурса: r-backend-vm-103011964
Данные для подключения к виртуальной машине. IP-адрес -- 81.26.184.148.
Данные для админки в foodgram/tests.yml

## Описание проекта

**Foodgram** – это полнофункциональное веб-приложение, «продуктовый помощник». Пользователи могут публиковать рецепты, подписываться на других авторов, добавлять рецепты в избранное, формировать список покупок и скачивать его в текстовом формате.

Проект реализован с отдельными backend (Django REST Framework) и frontend (React), развернутыми в Docker-контейнерах с использованием Nginx в качестве обратного прокси. Реализован CI/CD пайплайн на GitHub Actions для автоматического тестирования, сборки образов и деплоя на удалённый сервер.

## Функциональность

- **Регистрация и аутентификация пользователей** (Token-аутентификация через Djoser)
- **CRUD операции с рецептами**: создание, чтение, обновление, удаление
- **Загрузка изображений** для рецептов (base64)
- **Фильтрация рецептов** по автору, тегам, избранному и списку покупок
- **Пагинация** с настраиваемым количеством записей на странице
- **Избранное** – добавление рецептов в избранное
- **Список покупок** – добавление рецептов в корзину и скачивание сводного списка ингредиентов в формате TXT
- **Короткие ссылки** – генерация коротких ссылок на рецепты
- **Подписки** – подписка на авторов и просмотр их рецептов
- **Аватар пользователя** – загрузка и удаление аватара
- **Административная панель** Django для управления контентом
- **Автоматическое развертывание** через GitHub Actions
- **Интеграция с Telegram** для уведомлений об успешном деплое
- **Документация API** (ReDoc) по адресу `/api/docs/`

## Стек технологий

### Backend
- **Python 3.12**
- **Django 6.0.5** – веб-фреймворк
- **Django REST Framework 3.17.1** – API
- **PostgreSQL 16** – база данных
- **Gunicorn 26.0.0** – WSGI-сервер
- **Djoser 2.2.3** – аутентификация
- **django-filter 24.3** – фильтрация
- **django-cors-headers 4.9.0** – CORS
- **Pillow 12.2.0** – обработка изображений
- **psycopg2-binary 2.9.12** – драйвер PostgreSQL
- **SimpleJWT 5.5.1** – JWT-токены

### Frontend
- **React 17.0.2** – библиотека для построения UI
- **React Router DOM 5.3.0** – маршрутизация
- **CSS Modules** – стилизация компонентов
- **Fetch API** – взаимодействие с backend

### Инфраструктура
- **Docker** – контейнеризация
- **Docker Compose** – оркестрация контейнеров
- **Nginx 1.25.4** – веб-сервер и обратный прокси
- **GitHub Actions** – CI/CD
- **Telegram Bot API** – уведомления

## API Endpoints

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/auth/token/login/` | Вход (получение токена) |
| POST | `/api/auth/token/logout/` | Выход (удаление токена) |
| GET | `/api/users/` | Список пользователей |
| POST | `/api/users/` | Регистрация пользователя |
| GET | `/api/users/{id}/` | Профиль пользователя |
| GET | `/api/users/me/` | Текущий пользователь |
| POST | `/api/users/set_password/` | Смена пароля |
| PUT/DELETE | `/api/users/me/avatar/` | Управление аватаром |
| GET | `/api/users/subscriptions/` | Список подписок |
| POST/DELETE | `/api/users/{id}/subscribe/` | Подписка/отписка |
| GET | `/api/tags/` | Список тегов |
| GET | `/api/ingredients/` | Список ингредиентов |
| GET | `/api/recipes/` | Список рецептов |
| POST | `/api/recipes/` | Создание рецепта |
| GET | `/api/recipes/{id}/` | Детали рецепта |
| PATCH | `/api/recipes/{id}/` | Обновление рецепта |
| DELETE | `/api/recipes/{id}/` | Удаление рецепта |
| POST/DELETE | `/api/recipes/{id}/favorite/` | Избранное |
| POST/DELETE | `/api/recipes/{id}/shopping_cart/` | Список покупок |
| GET | `/api/recipes/{id}/get-link/` | Короткая ссылка |
| GET | `/api/recipes/download_shopping_cart/` | Скачать список покупок |

## Установка и развертывание

### Предварительные требования
- Docker и Docker Compose
- Git
- Аккаунт на Docker Hub (для публикации образов)
- Аккаунт на GitHub (для CI/CD)

### Локальный запуск (для разработки)

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Sibnum/foodgram.git
   cd foodgram
   ```

2. Создайте файл `.env` в корне проекта (см. раздел «Настройка переменных окружения»).

3. Запустите контейнеры:
   ```bash
   docker compose -f infra/docker-compose.yml up --build
   ```

4. Приложение будет доступно:
   - Frontend: `http://localhost`
   - API: `http://localhost/api/`
   - Админ-панель: `http://localhost/admin/`
   - Документация API: `http://localhost/api/docs/`

### Продуктивный деплой (с использованием CI/CD)

1. Настройте секреты в GitHub Actions:
   - `DOCKER_USERNAME` – логин Docker Hub
   - `DOCKER_PASSWORD` – пароль или токен доступа Docker Hub
   - `SERVER_HOST` – IP-адрес сервера
   - `SERVER_USER` – пользователь для SSH
   - `SSH_KEY` – приватный SSH-ключ
   - `TELEGRAM_TOKEN` – токен Telegram-бота
   - `TELEGRAM_USER_ID` – ID чата для уведомлений

2. Запушите изменения в ветку `main` – автоматически запустится workflow, который:
   - Запустит линтинг (flake8) и тесты Django
   - Соберет Docker-образы backend, frontend и gateway
   - Запушит образы в Docker Hub
   - Скопирует конфигурацию на сервер
   - Развернет приложение на сервере
   - Отправит уведомление в Telegram

## Настройка переменных окружения

Создайте файл `.env` в корне проекта со следующими переменными:

```env
# Django
SECRET_KEY=django-insecure-... (сгенерируйте свой)
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.ru
CORS_ALLOWED_ORIGINS=http://your-domain.ru

# PostgreSQL
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=strong_password_here
DB_HOST=db
DB_PORT=5432
```

**Важно:** Замените значения на свои, особенно `SECRET_KEY` и пароли.

## Импорт ингредиентов

При первом запуске backend автоматически импортирует ингредиенты из CSV-файла (`data/ingredients.csv`) в базу данных. Это выполняется скриптом `entrypoint.sh` при старте контейнера.

Для ручного импорта выполните:
```bash
docker exec -it foodgram_backend python manage.py import_data
```

## Создание суперпользователя

Для доступа к административной панели создайте суперпользователя:
```bash
docker exec -it foodgram_backend python manage.py createsuperuser
```

## Авторы

**Sibnum** – разработчик проекта.

- GitHub: [Sibnum](https://github.com/Sibnum)

**Команда Яндекс.Практикум** – образовательная платформа, в рамках которой создан проект.

## CI/CD и автоматическое тестирование

Проект использует GitHub Actions для автоматизации тестирования и деплоя. Файл workflow расположен в [`.github/workflows/main.yml`](.github/workflows/main.yml).

Workflow включает четыре джобы:
1. **tests** – линтинг (flake8) и запуск Django-тестов
2. **build_and_push** – сборка и публикация Docker-образов на Docker Hub
3. **deploy** – копирование конфигурации и деплой на сервер
4. **notify** – отправка уведомления в Telegram

### Чек-лист для проверки перед отправкой задания

- [ ] Проект доступен по доменному имени.
- [ ] Пуш в ветку main запускает тестирование, сборку образов и деплой.
- [ ] После успешного деплоя приходит сообщение в Telegram.
- [ ] Доступна документация API по адресу `/api/docs/`.
- [ ] Административная панель доступна по адресу `/admin/`.

## Лицензия

Проект распространяется под лицензией MIT. Подробности см. в файле [LICENSE](LICENSE).