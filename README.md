# DeliveryPizza

DeliveryPizza — это пример микросервисного приложения для доставки еды.
Проект включает backend на FastAPI, frontend на React + Vite и инфраструктуру на Docker Compose.

## 📌 Структура проекта

- `DeliveryPizza-backend/` — Backend-сервисы на Python/FastAPI
  - `auth/` — сервис аутентификации
  - `catalog/` — сервис меню и каталога блюд
  - `order/` — сервис заказов
  - `gateway/` — API-шлюз
  - `shared/` — общие модули (база данных, redis, схемы, безопасность)
- `DeliveryPizza-frontend/` — фронтенд-приложение на React + TypeScript + Vite
- `docker-compose.yml` — запуск всех сервисов и зависимостей
- `nginx/` — конфигурация прокси

## 🚀 Технологии

- Python 3.13 + FastAPI
- React + TypeScript + Vite
- PostgreSQL
- Redis
- Docker / Docker Compose
- SQLAlchemy
- Pydantic
- JWT

## 🧩 Архитектура

Система построена как набор микросервисов с единой точкой входа через API Gateway.
Backend-сервисы обмениваются данными через REST и используют PostgreSQL и Redis для хранения.

## ▶️ Быстрый запуск

Убедитесь, что установлены:
- Docker
- Docker Compose

В корне проекта выполните:

```bash
cd /home/v1po/develop/DeliveryPizza
docker-compose up -d
```

Для просмотра логов:

```bash
docker-compose logs -f
```

Остановить контейнеры:

```bash
docker-compose down
```

## 🔌 Доступные URL

- `http://localhost:8000` — API Gateway
- `http://localhost:8001/docs` — Swagger Auth Service
- `http://localhost:8002/docs` — Swagger Catalog Service
- `http://localhost:8003/docs` — Swagger Order Service

> Если используется `Redis Commander`, он может быть доступен на `http://localhost:8081`.

## 📂 Полезные файлы

- `DeliveryPizza-backend/README.md` — документация backend
- `DeliveryPizza-frontend/README.md` — документация frontend

## 💡 Примечания

- Фронтенд работает с API через `gateway`
- Настройки окружения и зависимости сервиса прописаны в его `Dockerfile` и `requirements.txt`
- Для разработки можно использовать локальные `docker-compose` сервисы с перенаправлением портов
