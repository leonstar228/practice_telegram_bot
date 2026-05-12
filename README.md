# TaskFlow Помічник

TaskFlow Помічник – Telegram-бот для автоматизації задач підприємства.  
Бот дозволяє створювати заявки, надсилати файли, переглядати статуси заявок та отримувати інформацію про погоду через API.

---

# Основні можливості

## Для користувачів

- створення нових заявок;
- перегляд власних заявок;
- редагування та видалення заявок;
- надсилання документів та фото;
- перегляд власних файлів;
- редагування назв файлів;
- видалення файлів;
- отримання інформації про погоду.

## Для адміністратора

- перегляд усіх активних заявок;
- зміна статусу заявок:
  - Нова
  - В роботі
  - Виконано
  - Відхилено

---

# Використані технології

- Python
- aiogram
- SQLite
- OpenWeather API

---

# Встановлення проєкту

## 1. Клонування репозиторію

```bash
git clone https://github.com/USERNAME/practice_telegram_bot.git
```

## 2. Перехід у папку проєкту

```bash
cd practice_telegram_bot
```

## 3. Створення віртуального середовища

```bash
python -m venv .venv
```

## 4. Активація середовища

### Windows

```bash
.\.venv\Scripts\activate
```

---

# Встановлення залежностей

```bash
pip install -r requirements.txt
```

---

# Налаштування .env

Створіть файл `.env` у корені проєкту:

```env
BOT_TOKEN=your_bot_token
ADMIN_IDS=your_telegram_id
WEATHER_API_KEY=your_weather_api_key
DB_PATH=bot.db
```

---

# Запуск бота

```bash
python main.py
```

---

# Структура проєкту

```text
practice_telegram_bot/
│
├── main.py
├── handlers.py
├── database.py
├── services.py
├── keyboards.py
├── states.py
├── config.py
├── requirements.txt
├── Procfile
├── runtime.txt
└── README.md
```

---

# База даних

У проєкті використовується SQLite.

Основні таблиці:
- users
- requests
- files

---

# API

Для отримання інформації про погоду використовується OpenWeather API:

https://openweathermap.org/api

---

# Автор

Проєкт розроблений у рамках навчальної практики.