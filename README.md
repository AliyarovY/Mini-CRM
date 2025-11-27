# Mini-CRM

Лёгкое CRM приложение с интеллектуальной системой распределения контактов, построенное на FastAPI и SQLAlchemy.

## Начало работы

### Требования
- Python 3.8+

### Установка

1. Создайте виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Запустите приложение:
```bash
uvicorn app.main:app --reload
```

API доступен по адресу `http://localhost:8000`
Документация доступна по адресу `http://localhost:8000/docs`

## Структура проекта

```
mini-crm/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI приложение & endpoints
│   ├── models.py        # SQLAlchemy ORM модели
│   ├── schemas.py       # Pydantic схемы запроса/ответа
│   ├── database.py      # Конфигурация БД & сессия
│   ├── crud.py          # CRUD операции
│   └── distribution.py  # Логика распределения контактов
├── crm.db               # SQLite база данных
├── requirements.txt     # Python зависимости
└── README.md
```

## Модели БД

### Operator
Представляет оператора, который обрабатывает контакты.
- `id` - Первичный ключ
- `name` - Уникальное имя оператора
- `is_active` - Статус активности
- `max_load` - Максимум контактов на оператора

### Source
Представляет источник лидов (например, сайт, телефон, email).
- `id` - Первичный ключ
- `name` - Уникальное имя источника
- `description` - Опциональное описание

### Lead
Представляет потенциального клиента.
- `id` - Первичный ключ
- `external_id` - Уникальный внешний идентификатор
- `phone` - Номер телефона контакта
- `email` - Email контакта
- `source_id` - Внешний ключ на Source
- `created_at` - Временная метка

### Contact
Представляет обращение лида к оператору.
- `id` - Первичный ключ
- `lead_id` - Внешний ключ на Lead
- `source_id` - Внешний ключ на Source
- `operator_id` - Внешний ключ на Operator (nullable если оператор недоступен)
- `is_active` - Статус активности
- `created_at` - Временная метка

### OperatorSourceWeight
Настраивает веса распределения операторов по источникам.
- `id` - Первичный ключ
- `operator_id` - Внешний ключ на Operator
- `source_id` - Внешний ключ на Source
- `weight` - Вес распределения (float)

## Алгоритм распределения

Система автоматически распределяет новые контакты операторам используя взвешенный случайный выбор:

1. **Получить доступных операторов**: Получить всех активных операторов, настроенных для источника
2. **Отфильтровать по нагрузке**: Исключить операторов, достигших лимита max_load
3. **Применить веса**: У каждого оператора есть вес для каждого источника
4. **Случайный выбор**: Выбрать оператора используя взвешенный случайный выбор (вероятность ∝ вес)
5. **Создать контакт**: Назначить выбранного оператора контакту

Если доступных операторов нет, контакт создается без назначения оператора.

## API Endpoints

### Операторы

#### Создать оператора
```bash
POST /operators
Content-Type: application/json

{
  "name": "Иван Петров",
  "is_active": true,
  "max_load": 5
}
```

#### Список операторов
```bash
GET /operators?skip=0&limit=100
```

#### Обновить оператора
```bash
PATCH /operators/{operator_id}
Content-Type: application/json

{
  "name": "Иван Сидоров",
  "is_active": true,
  "max_load": 10
}
```

### Источники

#### Создать источник
```bash
POST /sources
Content-Type: application/json

{
  "name": "Сайт",
  "description": "Лиды с формы на сайте"
}
```

#### Список источников
```bash
GET /sources?skip=0&limit=100
```

### Настройка весов

#### Установить вес оператора для источника
```bash
POST /sources/{source_id}/operators/{operator_id}/weight?weight=2.5
```

Вес - это число с плавающей точкой. Выше вес = выше вероятность выбора.

### Контакты и лиды

#### Создать лида с автоматическим распределением
```bash
POST /leads?external_id=LEAD123&phone=+1234567890&email=test@example.com&source_id=1

Ответ:
{
  "lead_id": 1,
  "external_id": "LEAD123",
  "phone": "+1234567890",
  "email": "test@example.com",
  "contact_id": 1,
  "operator_id": 1
}
```

#### Создать контакт для существующего лида
```bash
POST /contacts
Content-Type: application/json

{
  "lead_id": 1,
  "source_id": 1,
  "operator_id": null,
  "is_active": true
}
```

#### Список контактов
```bash
GET /contacts?skip=0&limit=100
```

#### Список лидов
```bash
GET /leads?skip=0&limit=100
```

### Статистика

#### Получить полную статистику
```bash
GET /stats

Ответ:
{
  "general": {
    "operators": 3,
    "sources": 2,
    "leads": 15,
    "contacts": 20,
    "active_contacts": 18
  },
  "operators_load": [
    {
      "operator_id": 1,
      "name": "Иван Петров",
      "current_load": 5,
      "max_load": 5
    }
  ],
  "source_distribution": [
    {
      "source_id": 1,
      "name": "Сайт",
      "contacts_count": 12
    }
  ]
}
```

## Пример использования

1. Создайте источники:
```bash
curl -X POST http://localhost:8000/sources \
  -H "Content-Type: application/json" \
  -d '{"name": "Сайт", "description": "Форма на сайте"}'
```

2. Создайте операторов:
```bash
curl -X POST http://localhost:8000/operators \
  -H "Content-Type: application/json" \
  -d '{"name": "Алиса", "is_active": true, "max_load": 5}'

curl -X POST http://localhost:8000/operators \
  -H "Content-Type: application/json" \
  -d '{"name": "Боб", "is_active": true, "max_load": 5}'
```

3. Установите веса распределения:
```bash
curl -X POST "http://localhost:8000/sources/1/operators/1/weight?weight=2.0"
curl -X POST "http://localhost:8000/sources/1/operators/2/weight?weight=1.0"
```

4. Создайте лидов (автоматически распределяются операторам):
```bash
curl -X POST "http://localhost:8000/leads?external_id=CUST001&phone=+1111111111&source_id=1"
curl -X POST "http://localhost:8000/leads?external_id=CUST002&phone=+2222222222&source_id=1"
```

5. Посмотрите статистику:
```bash
curl http://localhost:8000/stats
```
