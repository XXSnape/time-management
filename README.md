# 📝 Time Management Bot & WebApp

**Микросервисное приложение для управления задачами и привычками с Telegram-ботом и веб-интерфейсом**

---

## 🚀 О проекте

Данный проект — это система для управления задачами и привычками, включающая Telegram-бота, веб-интерфейс и сервисы для фоновых задач.  
Архитектура построена на микросервисах с использованием современных технологий Python.

---

## ⚙️ Технологический стек

- **Python** (FastAPI, Aiogram, SQLAlchemy, FastStream, APScheduler, PyJWT)
- **PostgreSQL** — основная база данных
- **Redis** — кэширование
- **RabbitMQ** — очередь сообщений
- **Docker**, **docker-compose**, **Nginx**
- **CI/CD** — GitHub Actions
- **Тестирование** — Pytest, Postman
- **Фронтенд** — HTML, CSS

---

## 📱 Функционал

### Telegram-бот 🤖
- Регистрация и аутентификация только через бота по Telegram ID (PyJWT)
- CRUD задач и привычек
- Напоминания о задачах и привычках (APScheduler)
- Команда `/stats` — статистика по задачам и привычкам
- Интеграция с внешним API для мотивационных цитат
- Гибкая настройка уведомлений
- Локализация (RU/EN)

### Веб-приложение 🌐
- Просмотр и управление задачами/привычками
- Визуализация статистики
- Админ-панель (SqlAdmin)
- Экспорт статистики в CSV (опция только в боте)

### Архитектура 🏗️
- Микросервисы: бот, API, сервис фоновых задач
- Чистая архитектура (паттерн Repository)
- Логирование и обработка ошибок

---

## 🐳 Быстрый старт (Docker)

1) 🗂️Клонируйте репозиторий:
```sh
git clone https://github.com/XXSnape/time-management.git
```
2) 🛠️Создайте файл `.env` на основе `.env.example` как в директории `backend/`, так и в директории `bot/`

Содержимое в backend можно просто перенести в .env, содержимое в bot нужно будет обязательно дополнить переменной `BOT_TOKEN`, а в остальном для локального запуска достаточно оставить переменные по умолчанию.

3) 🚀Запустите Docker Compose:
```sh
cd time-management
```

```sh
docker compose up
```

- Веб-интерфейс: http://localhost

По умолчанию логин и пароль для админа: `admin`

---

## 🧪 Тестирование


```sh
cd backend
```
🐍Создайте виртуальное окружение для python 3.12+ и установите зависимости:
```sh
pip install poetry
```
```sh
poetry install
```
⚠️Обязательно убедитесь, что во время запуска тестов запущена тестовая база, а в файле `.env` указаны параметры из `env.test`
Тестовую базу можно запустить с помощью Docker Compose:
```
cd backend
```

```sh
docker compose -f docker-compose.test.yml up
```

Если директории `backend\certs` с ключам еще не существует, запустите файл `backend\certs\create_certs.py` для создания сертификатов.

```sh
cd tests    
```

```sh
cd pytest -q
```


CI/CD: тесты и деплой запускаются автоматически при push в main.

---

## 📂 Структура репозитория

- `backend/` — исходный код API и веб-приложения
- `backend/nginx/` — конфигурация Nginx
- `bot/` — исходный код Telegram-бота
- `docker-compose.yml` — сборка и запуск всех сервисов
- `backend/tests/` — тесты Pytest

---

## 🛠️ Документация

- Swagger: http://localhost/docs
- Админ-панель: http://localhost/admin


---

## 💬 Локализация

- Русский 🇷🇺
- Английский en

---

## 📊 Примеры API

- Получить задачи: `GET /api/v1/tasks`
- Создать привычку: `POST /api/v1/habits`
- Получить статистику: `GET /api/v1/tasks/stats`

---

## 🏁 Параметры .env

- `DB_HOST` — адрес сервера базы данных PostgreSQL
- `DB_PORT` — порт для подключения к базе данных
- `POSTGRES_USER` — имя пользователя для доступа к базе данных
- `POSTGRES_PASSWORD` — пароль пользователя базы данных
- `POSTGRES_DB` — имя основной базы данных проекта
- `ADMIN_LOGIN` — логин администратора для входа в админ-панель
- `ADMIN_PASSWORD` — пароль администратора
- `ADMIN_TELEGRAM_ID` — Telegram ID администратора (должен быть бот для корректной работу)
- `BOT_TOKEN` — токен Telegram-бота для авторизации через [BotFather](https://t.me/BotFather)
- `BOT_LOGIN` — совпадает с `ADMIN_LOGIN`
- `BOT_PASSWORD` — совпадает с `ADMIN_PASSWORD`
- `REDIS_HOST` — адрес сервера Redis для кэширования и хранения сессий
- `REDIS_PORT` — порт Redis
- `RABBITMQ_DEFAULT_USER` — имя пользователя для очереди сообщений RabbitMQ
- `RABBITMQ_DEFAULT_PASS` — пароль пользователя RabbitMQ
- `RABBITMQ_HOST` — адрес сервера RabbitMQ
- `RABBITMQ_PORT` — порт RabbitMQ
- `BASE_API_URL` — базовый URL для обращения к API микросервисов

