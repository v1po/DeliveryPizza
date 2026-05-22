# Food Delivery Microservices Platform

Профессиональная микросервисная архитектура для системы доставки еды на FastAPI.

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                       API Gateway (:8000)                       │
│              (Rate Limiting, Routing, Load Balancing)           │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│  Auth Service │       │Catalog Service│       │ Order Service │
│    (:8001)    │       │    (:8002)    │       │    (:8003)    │
└───────────────┘       └───────────────┘       └───────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│  PostgreSQL   │       │     Redis     │       │Redis Commander│
│    (:5432)    │       │    (:6379)    │       │    (:8081)    │
└───────────────┘       └───────────────┘       └───────────────┘
```

## 🚀 Технологии

- **Python 3.13** - Последняя версия Python
- **FastAPI** - Современный асинхронный фреймворк
- **PostgreSQL 16** - Основная база данных
- **Redis 7** - Кэширование и сессии
- **Docker & Docker Compose** - Контейнеризация
- **SQLAlchemy 2.0** - Async ORM
- **Pydantic v2** - Валидация данных
- **JWT** - Аутентификация

## 📦 Сервисы

### Auth Service (`:8001`)
- Регистрация и авторизация пользователей
- JWT токены (access + refresh)
- Роли: customer, admin, manager, courier
- Blacklist токенов в Redis

### Catalog Service (`:8002`)
- Управление категориями меню
- Управление продуктами/блюдами
- Модификаторы (добавки к блюдам)
- Кэширование меню в Redis

### Order Service (`:8003`)
- Создание и управление заказами
- Статусы заказов с историей
- Интеграция с Catalog Service
- Статистика заказов

### API Gateway (`:8000`)
- Единая точка входа
- Rate Limiting
- Роутинг запросов
- Health checks

## 🛠️ Быстрый старт

### Требования
- Docker & Docker Compose
- (Опционально) Python 3.13 для локальной разработки

### Запуск всех сервисов

```bash
# Клонировать и перейти в директорию
cd food-delivery

# Запустить все сервисы
docker-compose up -d

# Посмотреть логи
docker-compose logs -f

# Остановить
docker-compose down
```

### Доступные URL

| Сервис | URL | Описание |
|--------|-----|----------|
| API Gateway | http://localhost:8000 | Основной API |
| Auth Docs | http://localhost:8001/docs | Swagger Auth |
| Catalog Docs | http://localhost:8002/docs | Swagger Catalog |
| Order Docs | http://localhost:8003/docs | Swagger Order |
| Redis Commander | http://localhost:8081 | UI для Redis |

## 📚 API Endpoints

### Аутентификация (`/api/v1/auth`)

```http
POST /api/v1/auth/register    # Регистрация
POST /api/v1/auth/login       # Вход
POST /api/v1/auth/refresh     # Обновление токена
POST /api/v1/auth/logout      # Выход
GET  /api/v1/auth/me          # Профиль
PATCH /api/v1/auth/me         # Обновить профиль
POST /api/v1/auth/me/password # Сменить пароль
```

### Каталог (`/api/v1/categories`, `/api/v1/products`, `/api/v1/menu`)

```http
# Категории
GET  /api/v1/categories          # Дерево категорий
GET  /api/v1/categories/{id}     # Категория по ID
POST /api/v1/categories          # Создать (admin)
PATCH /api/v1/categories/{id}    # Обновить (admin)
DELETE /api/v1/categories/{id}   # Удалить (admin)

# Продукты
GET  /api/v1/products            # Список с фильтрами
GET  /api/v1/products/featured   # Популярные
GET  /api/v1/products/{id}       # Продукт по ID
POST /api/v1/products            # Создать (admin)
PATCH /api/v1/products/{id}      # Обновить (admin)
DELETE /api/v1/products/{id}     # Удалить (admin)

# Меню
GET /api/v1/menu                 # Полное меню (cached)
```

### Заказы (`/api/v1/orders`)

```http
POST /api/v1/orders              # Создать заказ
GET  /api/v1/orders/my           # Мои заказы
GET  /api/v1/orders/{id}         # Заказ по ID
PATCH /api/v1/orders/{id}        # Обновить (pending)
POST /api/v1/orders/{id}/cancel  # Отменить
GET  /api/v1/orders/{id}/history # История статусов

# Admin
GET  /api/v1/admin/orders           # Все заказы
PATCH /api/v1/admin/orders/{id}/status  # Изменить статус
GET  /api/v1/admin/orders/statistics    # Статистика
```

## 🔐 Аутентификация

### Регистрация
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "Password123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Вход
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "Password123"
  }'
```

### Использование токена
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## 📊 Примеры

### Создание заказа
```bash
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 3, "quantity": 1}
    ],
    "delivery_type": "delivery",
    "delivery_address": "ул. Примерная, д. 1",
    "contact_name": "Иван Иванов",
    "contact_phone": "+7999123456",
    "payment_method": "card"
  }'
```

## 🧪 Локальная разработка

### Создание виртуального окружения
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r services/auth/requirements.txt
```

### Запуск отдельного сервиса
```bash
cd services/auth
uvicorn app.main:app --reload --port 8001
```

## 📁 Структура проекта

```
├── docker-compose.yml
├── README.md
├── scripts/
│   └── init-databases.sh
├── shared/
│   ├── __init__.py
│   ├── database.py
│   ├── redis_client.py
│   ├── schemas.py
│   ├── security.py
│   └── exceptions.py
└── services/
    ├── auth/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── app/
    │       ├── __init__.py
    │       ├── config.py
    │       ├── models.py
    │       ├── schemas.py
    │       ├── repository.py
    │       ├── service.py
    │       ├── dependencies.py
    │       ├── routes.py
    │       └── main.py
    ├── catalog/
    │   └── ... (аналогичная структура)
    ├── order/
    │   └── ... (аналогичная структура)
    └── gateway/
        └── ... (аналогичная структура)
```

## ⚙️ Переменные окружения

### Auth Service
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/auth_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Catalog Service
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/catalog_db
REDIS_URL=redis://localhost:6379
```

### Order Service
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/order_db
REDIS_URL=redis://localhost:6379
CATALOG_SERVICE_URL=http://catalog:8002
AUTH_SERVICE_URL=http://auth:8001
```

## 🔄 Статусы заказов

```
PENDING → CONFIRMED → PREPARING → READY → DELIVERING → DELIVERED
    ↓         ↓           ↓         ↓          ↓
    └─────────┴───────────┴─────────┴──────────┴──→ CANCELLED
```

## 📈 Масштабирование

```bash
# Масштабировать catalog сервис до 3 инстансов
docker-compose up -d --scale catalog=3
```

## 📝 License

MIT
